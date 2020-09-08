flake: { config, pkgs, lib, ... }:

with lib;

let
  cfg = config.services.prometheus-fritzscraper-exporter;
in {
  options.services.prometheus-fritzscraper-exporter =  {
    enable = mkEnableOption "prometheus-fritzscraper-exporter";

    listenPort = mkOption {
      type = types.int;
      default = 8140;
      description = "Port that the FRITZ!Scraper Prometheus exporter listens on";
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
    systemd.services."prometheus-fritzscraper-exporter" = let
      pkg = flake.defaultPackage."${system}";
    in {
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];
      serviceConfig.Restart = mkDefault "always";
      serviceConfig.PrivateTmp = mkDefault true;
      serviceConfig.WorkingDirectory = mkDefault "/tmp";

      serviceConfig.ExecStart = ''
        ${pkg}/bin/prometheus-fritzscraper-exporter \
          ${toString cfg.listenPort} ${cfg.gatewayAddress} ${cfg.username} ${cfg.password}
      '';
    };
  };
}
