{
  description = "AVM FRITZ!Box status scraper and Prometheus exporter";

  outputs = { self, nixpkgs }: let
    pkgs = import nixpkgs {
      system = "x86_64-linux";
      overlays = [ self.overlay ];
    };
  in {
    overlay = final: prev: {
      prometheus-fritzscraper-exporter = final.poetry2nix.mkPoetryApplication {
        projectDir = ./.;
        shellHook = " "; # The pipShellHook causes problems without a setup.py
        python = final.python38;
      };
    };

    defaultPackage.x86_64-linux = pkgs.prometheus-fritzscraper-exporter;

    nixosModules.prometheus-fritzscraper-exporter = import ./module.nix self;
  };
}
