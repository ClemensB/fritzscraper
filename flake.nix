{
  description = "AVM FRITZ!Box status scraper and Prometheus exporter";

  inputs.nixpkgs.follows = "nix/nixpkgs";

  outputs = { self, nix, nixpkgs }: let
    pkgs = import nixpkgs {
      system = "x86_64-linux";
      overlays = [ self.overlay nix.overlay ];
    };
  in {
    overlay = final: prev: {
      prometheus-fritzscraper-exporter = final.python3Packages.buildPythonApplication {
        pname = "fritzscraper";
        version = "0.0.1";

        src = ./.;

        propagatedBuildInputs = with final.python3Packages; [
          pandas
          prometheus_client
          requests
        ];
      };
    };

    defaultPackage.x86_64-linux = pkgs.prometheus-fritzscraper-exporter;

    nixosModules.prometheus-fritzscraper-exporter = { config, pkgs, lib, ... }: with lib; let
      cfg = config.services.prometheus-fritzscraper-exporter;
    in {
      options.services.prometheus-fritzscraper-exporter =  {
        enable = mkEnableOption "prometheus-fritzscraper-exporter";

        listenPort = mkOption {
          type = types.int;
          default = 8140;
          description = "Port that the FRITZ!Scraper Promtheus exporter listens on";
        };

        gatewayAddress = mkOption {
          type = types.str;
          default = "fritz.box";
          description = ''
            The hostname or IP of the FRITZ!Box.
          '';
        };

        username = mkOption {
          type = types.str;
          default = "root";
          description = ''
            The username to used authenticate with the FRITZ!Box.
          '';
        };

        password = mkOption {
          type = types.str;
          default = "";
          description = ''
            The password to used authenticate with the FRITZ!Box.
          '';
        };
      };

      config = mkIf cfg.enable {
        # nixpkgs.overlays = [ self.overlay ];

        systemd.services."prometheus-fritzscraper-exporter" = let
          myPkgs = pkgs.appendOverlays [ self.overlay ];
        in {
          wantedBy = [ "multi-user.target" ];
          after = [ "network.target" ];
          serviceConfig.Restart = mkDefault "always";
          serviceConfig.PrivateTmp = mkDefault true;
          serviceConfig.WorkingDirectory = mkDefault "/tmp";

          serviceConfig.ExecStart = ''
            ${myPkgs.prometheus-fritzscraper-exporter}/bin/prometheus-fritzscraper-exporter \
              ${toString cfg.listenPort} ${cfg.gatewayAddress} ${cfg.username} ${cfg.password}
          '';
        };
      };
    };
  };
}
