with import <nixpkgs> {};
stdenv.mkDerivation rec {
  name = "misas";
  env = buildEnv { name = name; paths = buildInputs; };
  fastscript = python3.pkgs.buildPythonPackage rec {
    pname = "fastscript";
    version = "0.1.4";
    src = builtins.fetchGit {
      rev = "c217e613824c5219a1035faf9b8f0b11ae64c067";
      url = "https://github.com/fastai/fastscript";
      #inherit pname version;
      #sha256 = "16m1ifr0ymf2wk2rvcrza3p6cvs21cl408fp0m03s1mc2ydlgzd0";
    };
    propagatedBuildInputs = [
      python3Packages.packaging
    ];
    doCheck = false;
  };
  nbdev = python3.pkgs.buildPythonPackage rec {
    pname = "nbdev";
    version = "0.2.18";
    src = python3.pkgs.fetchPypi {
    #src = builtins.fetchGit {
      #rev = "c8729bbcf1ed8ca31ee4d16c33935b5f44b74997";
      #url = "https://github.com/fastai/nbdev";
      inherit pname version;
      sha256 = "1ya9q3b3fya03hhqi3y5cipcr534xky47n3y2y6rzv5xay0ipy6j";
    };
    propagatedBuildInputs = [
      python3Packages.nbconvert
      python3Packages.pyyaml
      fastscript
    ];
    doCheck = false;
  };
  buildInputs = [
    python3
    # python3Packages.pandas
    nbdev
  ];
}
