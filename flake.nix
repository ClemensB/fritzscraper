{
  description = "AVM FRITZ!Box status scraper and Prometheus exporter";

  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }: {
    overlay = final: prev: {
      fritzscraper = final.poetry2nix.mkPoetryApplication {
        projectDir = ./.;
        shellHook = " "; # The pipShellHook causes problems without a setup.py
        python = final.python38;
      };
    };

    nixosModules.prometheus-fritzscraper-exporter = import ./module.nix self;

  } // flake-utils.lib.eachDefaultSystem (system: let
    pkgs = import nixpkgs { inherit system; overlays = [ self.overlay ]; };
  in {
    packages = {
      inherit (pkgs) fritzscraper;
    };

    defaultPackage = self.packages."${system}".fritzscraper;
  });
}
