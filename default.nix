with import <nixpkgs> {};
python3.pkgs.buildPythonPackage {
  name = "env";
  src = ./.;
  propagatedBuildInputs = with python3.pkgs;[
    docopt
    requests
    beautifulsoup4
    notify2
    (callPackage ./straight-plugin.nix {})
  ];
  checkInputs = [ python3.pkgs.black ];
}
