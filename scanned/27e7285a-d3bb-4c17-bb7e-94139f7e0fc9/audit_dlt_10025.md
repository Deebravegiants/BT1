# [?] Merge branch 'main' into mikhail/fix-indexer-runtime-crash

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-09-20
Source: https://github.com/movement-network/movement/commit/f079694ddfa246850e31dda6ba79a644579361c9
Type: security-commit

## Details
Merge branch 'main' into mikhail/fix-indexer-runtime-crash

## Patch
### .github/workflows/checks-all.yml
```diff
@@ -32,6 +32,11 @@ jobs:
     - name: Install Nix
       uses: DeterminateSystems/nix-installer-action@main
 
+    - uses: cachix/cachix-action@v15
+      with:
+        name: movementlabs
+        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
+
     - name: Run Cargo Check in nix environment
       run: |
         nix develop --command bash  -c "cargo check --all-targets"  
@@ -86,12 +91,42 @@ jobs:
     - name: Install Nix
       uses: DeterminateSystems/nix-installer-action@main
 
+    - uses: cachix/cachix-action@v15
+      with:
+        name: movementlabs
+        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
+
     - name: Run Suzuka Full Node Tests Against Local ETH and Local Celestia
       env:
         CELESTIA_LOG_LEVEL: FATAL # adjust the log level while debugging
       run: |
         nix develop --command bash  -c "just suzuka-full-node native build.setup.eth-local.celestia-local.test -t=false"
-        nix develop --command bash  -c "just suzuka-full-node native build.setup.eth-local.celestia-local.test -t=false"  
+
+  suzuka-indexer-local:
+    if: github.event.label.name == 'cicd:suzuka-full-node' ||  github.ref == 'refs/heads/main'
+    strategy:
+      matrix:
+        include:
+          - os: ubuntu-22.04
+            arch: x86_64
+            runs-on: buildjet-16vcpu-ubuntu-2204
+
+    runs-on: ${{ matrix.runs-on }}
+
+    steps:
+    - name: Checkout repository
+      uses: actions/checkout@v4
+      with:
+        submodules: true
+
+    - name: Install Nix
+      uses: DeterminateSystems/nix-installer-action@main
+
+    - name: Run Suzuka Full Node + indexer Tests Against Local ETH and Local Celestia
+      env:
+        CELESTIA_LOG_LEVEL: FATAL # adjust the log level while debugging
+      run: |
+        nix develop --command bash  -c "just suzuka-full-node native build.celestia-local.indexer.hasura.indexer-test -t=false"
   
   suzuka-full-node-remote:
     if: false 
@@ -113,6 +148,11 @@ jobs:
     - name: Install Nix
       uses: DeterminateSystems/nix-installer-action@main
 
+    - uses: cachix/cachix-action@v15
+      with:
+        name: movementlabs
+        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
+
     - name: Run Suzuka Full Node Tests Against Holesky and Local Celestia
       env: 
         CELESTIA_LOG_LEVEL: FATAL # adjust the log level while debugging
@@ -139,6 +179,11 @@ jobs:
     - name: Install Nix
       uses: DeterminateSystems/nix-installer-action@main
 
+    - uses: cachix/cachix-action@v15
+      with:
+        name: movementlabs
+        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
+
     - name: Run M1 DA Light Node tests in nix environment
       # adjust the log level while debugging
       run: CELESTIA_LOG_LEVEL=FATAL nix develop --command bash  -c "just m1-da-light-node native build.setup.test.local -t=false"  
@@ -165,6 +210,12 @@ jobs:
     - name: Install Nix
       uses: DeterminateSystems/nix-installer-action@main
 
+
+    - uses: cachix/cachix-action@v15
+      with:
+        name: movementlabs
+        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
+
     - name: Run MCR Client Tests
       run: nix develop --command bash  -c "just mcr-client native build.local.test -t=false"
 
@@ -190,6 +241,11 @@ jobs:
     - name: Install Nix
       uses: DeterminateSystems/nix-installer-action@main
 
+    - uses: cachix/cachix-action@v15
+      with:
+        name: movementlabs
+        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
+
     - name: Run Aptos Tests
       run: |
         nix develop --command bash -c "
@@ -219,6 +275,11 @@ jobs:
     - name: Install Nix
       uses: DeterminateSystems/nix-installer-action@main
 
+    - uses: cachix/cachix-action@v15
+      with:
+        name: movementlabs
+        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
+
     - name: Run rust tests
       run: |
         nix develop --command bash -c "
@@ -243,6 +304,11 @@ jobs:
     - name: Install Nix
       uses: DeterminateSystems/nix-installer-action@main
 
+    - uses: cachix/cachix-action@v15
+      with:
+        name: movementlabs
+        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
+
     - name: Run foundry tests
       run: |
         nix develop --command bash -c "
@@ -288,6 +354,11 @@ jobs:
     - name: Install Nix
       uses: DeterminateSystems/nix-installer-action@main
 
+    - uses: cachix/cachix-action@v15
+      with:
+        name: movementlabs
+        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
+
     - name: Run eth_movement tests
       run: |
         nix develop --command bash -c "rust_backtrace=1 cargo test --test eth_movement -- --nocapture --test-threads=1"
```

### .gitmodules
```diff
@@ -34,3 +34,24 @@
 [submodule "protocol-units/settlement/mcr/contracts/lib/murky"]
 	path = protocol-units/settlement/mcr/contracts/lib/murky
 	url = https://github.com/dmfxyz/murky
+[submodule "protocol-units/settlement/mcr/contracts/lib/safe-smart-account"]
+	path = protocol-units/settlement/mcr/contracts/lib/safe-smart-account
+	url = https://github.com/safe-global/safe-smart-account
+[submodule "bridge-forge-std"]
+	path = protocol-units/bridge/contracts/lib/forge-std
+	url = https://github.com/foundry-rs/forge-std
+[submodule "bridge-openzeppelin-contracts"]
+	path = protocol-units/bridge/contracts/lib/openzeppelin-contracts
+	url = https://github.com/OpenZeppelin/openzeppelin-contracts
+[submodule "bridge-openzeppelin-contracts-upgradeable"]
+	path = protocol-units/bridge/contracts/lib/openzeppelin-contracts-upgradeable
+	url = https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable
+[submodule "dispute-forge-std"]
+	path = protocol-units/dispute/lib/forge-std
+	url = https://github.com/foundry-rs/forge-std
+[submodule "dispute-openzeppelin-contracts"]
+	path = protocol-units/dispute/lib/openzeppelin-contracts
+	url = https://github.com/OpenZeppelin/openzeppelin-contracts
+[submodule "dispute-murky"]
+	path = protocol-units/dispute/lib/murky
+	url = https://github.com/dmfxyz/murky
```

### Cargo.lock
```diff
@@ -1966,7 +1966,7 @@ dependencies = [
 [[package]]
 name = "aptos-moving-average"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=656bb2ba08888cba4d16405b8b668155a5c624eb#656bb2ba08888cba4d16405b8b668155a5c624eb"
+source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58#1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58"
 dependencies = [
  "chrono",
 ]
@@ -3567,9 +3567,9 @@ dependencies = [
 
 [[package]]
 name = "blockstore"
-version = "0.7.0"
+version = "0.6.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7679095248a6dc7555fae81154ed1baef264383c16621ef881a219576c72a9be"
+checksum = "dc99329facbb960effbe7ed707c753a718877c1878eb8ca08704fa391c494020"
 dependencies = [
  "cid",
  "dashmap 6.1.0",
@@ -3988,7 +3988,8 @@ dependencies = [
 [[package]]
 name = "celestia-proto"
 version = "0.3.0"
-source = "git+https://github.com/eigerco/lumina#dae322c4c13e66c468a94d5aa208ab4fd4e30ae8"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9d7bb5f52d67256ed0545271bb3bbe33f106576884e6acc3cfaedc5bb78c41d3"
 dependencies = [
  "anyhow",
  "celestia-tendermint-proto",
@@ -4000,8 +4001,9 @@ dependencies = [
 
 [[package]]
 name = "celestia-rpc"
-version = "0.4.0"
-source = "git+https://github.com/eigerco/lumina#dae322c4c13e66c468a94d5aa208ab4fd4e30ae8"
+version = "0.3.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "5110ce517363b075f3880f4bc88fd1f5c0b3f711a11daa3c34c66da7ae94b9a7"
 dependencies = [
  "async-trait",
  "celestia-types",
@@ -4014,9 +4016,9 @@ dependencies = [
 
 [[package]]
 name = "celestia-tendermint"
-version = "0.32.2"
+version = "0.32.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ce8c92a01145f79a0f3ac7c44a43a9b5ee58e8a4c716b56d98833a3848db1afd"
+checksum = "95f93b5cbbd62b6cfde961889bf05d5fe19e70d8500c4465694306ed2695ac23"
 dependencies = [
  "bytes 1.7.1",
  "celestia-tendermint-proto",
@@ -4043,9 +4045,9 @@ dependencies = [
 
 [[package]]
 name = "celestia-tendermint-proto"
-version = "0.32.2"
+version = "0.32.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9a95746c5221a74d7b913a415fdbb9e7c90e1b4d818dbbff59bddc034cfce2ec"
+checksum = "b8f7d49c1ececa30a4587c5fe8a4035b786b78a3253ed0f9636de591b3dc2b37"
 dependencies = [
  "bytes 1.7.1",
  "flex-error",
@@ -4061,8 +4063,9 @@ dependencies = [
 
 [[package]]
 name = "celestia-types"
-version = "0.4.0"
-source = "git+https://github.com/eigerco/lumina#dae322c4c13e66c468a94d5aa208ab4fd4e30ae8"
+version = "0.3.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "08e6a207db787043faf6b630e2caa365d5be1b72553d541a75cfd4e17086191c"
 dependencies = [
  "base64 0.22.1",
  "bech32",
@@ -10635,13 +10638,13 @@ dependencies = [
 [[package]]
 name = "processor"
 version = "1.0.0"
-source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=656bb2ba08888cba4d16405b8b668155a5c624eb#656bb2ba08888cba4d16405b8b668155a5c624eb"
+source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58#1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58"
 dependencies = [
  "ahash 0.8.11",
  "allocative",
  "allocative_derive",
  "anyhow",
- "aptos-moving-average 0.1.0 (git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=656bb2ba08888cba4d16405b8b668155a5c624eb)",
+ "aptos-moving-average 0.1.0 (git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58)",
  "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=338f9a1bcc06f62ce4a4994f1642b9a61b631ee0)",
  "async-trait",
  "bcs 0.1.4",
@@ -12143,7 +12146,7 @@ dependencies = [
 [[package]]
 name = "server-framework"
 version = "1.0.0"
-source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=656bb2ba08888cba4d16405b8b668155a5c624eb#656bb2ba08888cba4d16405b8b668155a5c624eb"
+source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58#1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58"
 dependencies = [
  "anyhow",
  "aptos-system-utils",
@@ -12852,6 +12855,7 @@ dependencies = [
  "num_cpus",
  "processor",
  "reqwest 0.12.7",
+ "serde_json",
  "server-framework",
  "tempfile",
  "tokio",
```

### Cargo.toml
```diff
@@ -148,8 +148,8 @@ aptos-indexer-grpc-table-info = { git = "https://github.com/movementlabsxyz/apto
 aptos-protos = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
 
 # Indexer
-processor = { git = "https://github.com/movementlabsxyz/aptos-indexer-processors", rev = "656bb2ba08888cba4d16405b8b668155a5c624eb", subdir = "rust" }
-server-framework = { git = "https://github.com/movementlabsxyz/aptos-indexer-processors", rev = "656bb2ba08888cba4d16405b8b668155a5c624eb", subdir = "rust" }
+processor = { git = "https://github.com/movementlabsxyz/aptos-indexer-processors", rev = "1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58", subdir = "rust" }
+server-framework = { git = "https://github.com/movementlabsxyz/aptos-indexer-processors", rev = "1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58", subdir = "rust" }
 
 bcs = { git = "https://github.com/aptos-labs/bcs.git", rev = "d31fab9d81748e2594be5cd5cdf845786a30562d" }
 ethereum-types = "0.14.1"
@@ -179,8 +179,10 @@ secp256k1 = { version = "0.27", default-features = false, features = [
 ] }
 
 ## Celestia Dependencies
-celestia-rpc = { git = "https://github.com/eigerco/lumina" }
-celestia-types = { git = "https://github.com/eigerco/lumina" }
+#celestia-rpc = { git = "https://github.com/eigerco/lumina" }
+#celestia-types = { git = "https://github.com/eigerco/lumina", version= "0.2.x" }
+celestia-types = "0.3.0"
+celestia-rpc = "0.3.0"
 
 
 alloy = { git = "https://github.com/alloy-rs/alloy.git", package = "alloy", rev = "83343b172585fe4e040fb104b4d1421f58cbf9a2", features = [
```

### docker/compose/suzuka-full-node/docker-compose.yml
```diff
@@ -46,6 +46,7 @@ services:
       - DOT_MOVEMENT_PATH=/.movement
       - MOVEMENT_TIMING=info
       - M1_DA_LIGHT_NODE_TIMING_LOG=/.movement/m1-da-light-node-timing.log
+      - RUST_BACKTRACE=1
     volumes:
       - ${DOT_MOVEMENT_PATH}:/.movement
     depends_on:
@@ -67,6 +68,7 @@ services:
       - DOT_MOVEMENT_PATH=/.movement
       - MOVEMENT_TIMING=info
       - SUZUKA_TIMING_LOG=/.movement/suzuka-timing.log
+      - RUST_BACKTRACE=1
     volumes:
       - ${DOT_MOVEMENT_PATH}:/.movement
     depends_on:
@@ -87,6 +89,7 @@ services:
     command: run-simple
     environment:
       - DOT_MOVEMENT_PATH=/.movement
+      - RUST_BACKTRACE=1
     volumes:
       - ${DOT_MOVEMENT_PATH}:/.movement
     ports:
```

### docker/compose/suzuka-indexer/docker-compose.hasura.yml
```diff
@@ -12,7 +12,7 @@ services:
       HASURA_GRAPHQL_METADATA_DATABASE_URL: postgresql://postgres:password@${POSTGRES_DB_HOST}:5432/postgres
       HASURA_GRAPHQL_DATABASE_URL: postgresql://postgres:password@postgres:5432/${POSTGRES_DB_HOST}
       ## this env var can be used to add the above postgres database to Hasura as a data source. this can be removed/updated based on your needs
-      PG_DATABASE_URL: postgres://postgres:postgres:password@postgres:5432/${POSTGRES_DB_HOST}
+      PG_DATABASE_URL: postgres://postgres:postgres:password@${POSTGRES_DB_HOST}:5432/postgres
       ## enable the console served by server
       HASURA_GRAPHQL_ENABLE_CONSOLE: "true" # set to "false" to disable console
       ## enable debugging mode. It is recommended to disable this in production
```

### docker/compose/suzuka-indexer/docker-compose.indexer.yml
```diff
@@ -31,7 +31,7 @@ services:
       - INDEXER_PROCESSOR_POSTGRES_CONNECTION_STRING=${INDEXER_PROCESSOR_POSTGRES_CONNECTION_STRING}
     volumes:
       - ${DOT_MOVEMENT_PATH}:/.movement
-    restart: on-failure:5
+    restart: always
     depends_on:
       - postgres
 
```

### flake.lock
```diff
@@ -7,11 +7,11 @@
         ]
       },
       "locked": {
-        "lastModified": 1717025063,
-        "narHash": "sha256-dIubLa56W9sNNz0e8jGxrX3CAkPXsq7snuFA/Ie6dn8=",
+        "lastModified": 1721842668,
+        "narHash": "sha256-k3oiD2z2AAwBFLa4+xfU+7G5fisRXfkvrMTCJrjZzXo=",
         "owner": "ipetkov",
         "repo": "crane",
-        "rev": "480dff0be03dac0e51a8dfc26e882b0d123a450e",
+        "rev": "529c1a0b1f29f0d78fa3086b8f6a134c71ef3aaf",
         "type": "github"
       },
       "original": {
```

### flake.nix
```diff
@@ -9,184 +9,119 @@
     
   };
 
-  outputs = {
-    self,
-    nixpkgs,
-    rust-overlay,
-    flake-utils,
-    foundry,
-    crane,
-    ...
-    }:
-    flake-utils.lib.eachSystem ["aarch64-darwin" "x86_64-darwin" "x86_64-linux" "aarch64-linux"] (
-
-      system: let
-        overrides = (builtins.fromTOML (builtins.readFile ./rust-toolchain.toml));
-
-        overlays = [
-          (import rust-overlay)
-          foundry.overlay
-        ];
-
+  outputs = { nixpkgs, rust-overlay, flake-utils, foundry, crane, ... }:
+    flake-utils.lib.eachDefaultSystem (system:
+      let
         pkgs = import nixpkgs {
-          inherit system overlays;
+          inherit system;
+          overlays = [ (import rust-overlay) foundry.overlay ];
         };
 
-        craneLib = crane.mkLib pkgs;
-
-        frameworks = pkgs.darwin.apple_sdk.frameworks;
-
-        buildDependencies = with pkgs; [
-          llvmPackages.bintools
-          openssl
-          openssl.dev
-          libiconv 
-          pkg-config
-          libclang.lib
-          libz
-          clang
-          pkg-config
-          protobuf
-          rustPlatform.bindgenHook
-          lld
-          mold
-          coreutils
-          gcc
-          rust
-          postgresql
-        ];
-        
-        sysDependencies = with pkgs; [] 
-        ++ lib.optionals stdenv.isDarwin [
-          frameworks.Security
-          frameworks.CoreServices
-          frameworks.SystemConfiguration
-          frameworks.AppKit
-          libelf
-        ] ++ lib.optionals stdenv.isLinux [
-          udev
-          systemd
-          snappy
-          bzip2
-          elfutils
-        ];
-
-        testDependencies = with pkgs; [
-          python311
-          poetry
-          just
-          foundry-bin
-          process-compose
-          celestia-node
-          celestia-app
-          monza-aptos
-          jq
-          docker
-          solc
-          grpcurl
-          grpcui
-        ];
-
-        # Specific version of toolchain
-        rust = pkgs.rust-bin.fromRustupToolchainFile ./rust-toolchain.toml;
-
-        rustPlatform = pkgs.makeRustPlatform {
-          cargo = rust;
-          rustc = rust;
+        toolchain = p: (p.rust-bin.fromRustupToolchainFile ./rust-toolchain.toml).override {
+          extensions = [ "rustfmt" ];
         };
+        craneLib = (crane.mkLib pkgs).overrideToolchain(toolchain);
 
-        # Needs to be removed soon and replaced with aptos-faucet-service
-        monza-aptos = pkgs.stdenv.mkDerivation {
-            pname = "monza-aptos";
-            version = "branch-monza";
-
-            src = pkgs.fetchFromGitHub {
-                owner = "movementlabsxyz";
-                repo = "aptos-core";
-                rev = "06443b81f6b8b8742c4aa47eba9e315b5e6502ff";
-                sha256 = "sha256-iIYGbIh9yPtC6c22+KDi/LgDbxLEMhk4JJMGvweMJ1Q=";
-            };
-
-            installPhase = ''
-                cp -r . $out
-            '';
+        monza-aptos = pkgs.fetchgit {
+          url = "https://github.com/movementlabsxyz/aptos-core";
+          rev = "06443b81f6b8b8742c4aa47eba9e315b5e6502ff";
+          hash = "sha256-W42uBu2A1ctlI07eWEGxtf0T8NgH03SPJkYSBly4zZ4=";
+        };
 
-            meta = with pkgs.lib; {
-                description = "Aptos core repository on the monza branch";
-                homepage = "https://github.com/movementlabsxyz/aptos-core";
-                license = licenses.asl20;
-            };
+        aptos-faucet-service-common-args = {
+          pname = "aptos-faucet-service";
+          version = "2.0.1";
+          
+          src = monza-aptos;
+          strictDeps = true;
+
+          nativeBuildInputs = with pkgs; [
+            pkg-config
+          ];
+          buildInputs = with pkgs; [
+            openssl
+            systemd
+            rocksdb
+            rustPlatform.bindgenHook
+          ];
         };
-        # Remember, remove this thing above
-        
-        # celestia-node
-        celestia-node = import ./nix/celestia-node.nix { inherit pkgs; };
-
-        # celestia-app
-        celestia-app = import ./nix/celestia-app.nix { inherit pkgs; };
-
-        # aptos-faucet-service
-        aptos-faucet-service = import ./nix/aptos-faucet-service.nix { 
-          inherit pkgs; 
-          commonArgs = {
-            src = pkgs.fetchFromGitHub {
-              owner = "movementlabsxyz";
-              repo = "aptos-core";
-              rev = "06443b81f6b8b8742c4aa47eba9e315b5e6502ff";
-              sha256 = "sha256-iIYGbIh9yPtC6c22+KDi/LgDbxLEMhk4JJMGvweMJ1Q=";
-            };
-            strictDeps = true;
-            
-            buildInputs = with pkgs; [] ++buildDependencies ++ sysDependencies;
-            nativeBuildInputs = with pkgs; [] ++buildDependencies ++sysDependencies;
+        aptos-faucet-service-deps = craneLib.buildDepsOnly aptos-faucet-service-common-args;
+        aptos-faucet-service = craneLib.buildPackage (aptos-faucet-service-common-args // {
+          cargoArtifacts = aptos-faucet-service-deps;
+          cargoExtraArgs = "-p aptos-faucet-service";
+        });
+
+        celestia-app = pkgs.buildGoModule {
+          pname = "celestia-app";
+          version = "1.8.0";
+
+          src = pkgs.fetchgit {
+            url = "https://github.com/celestiaorg/celestia-app";
+            rev = "e75a1fdc8f2386d9f389cb596c88ca7cc19563af";
+            hash = "sha256-EE9r1sybbm4Hyh57/nC8utMx/uFdMsIdPecxBtDqAbk=";
           };
-          inherit craneLib;
-        };
-    
-      in
-        with pkgs; {
 
-          packages.aptos-faucet-service = aptos-faucet-service;
+          vendorHash = "sha256-2vU1liAm0us7Nk1eawgMvarhq77+IUS0VE61FuvQbuQ=";
+          subPackages = [ "cmd/celestia-appd" ];
+        };
 
-          packages.celestia-node = celestia-node;
+        celestia-node = pkgs.buildGoModule {
+          pname = "celestia-node";
+          version = "0.13.3";
 
-          packages.celestia-app = celestia-app;
-          
-          # Used for workaround for failing vendor dep builds in nix
-          devShells.docker-build = mkShell {
-            buildInputs = [] ++buildDependencies ++sysDependencies;
-            nativeBuildInputs = [] ++buildDependencies ++sysDependencies;
-            OPENSSL_DEV=pkgs.openssl.dev;
-            PKG_CONFIG_PATH = "${pkgs.openssl.dev}/lib/pkgconfig";
-            SNAPPY = if stdenv.isLinux then pkgs.snappy else null;
-            shellHook = ''
-              #!/usr/bin/env bash
-              echo "rust-build shell"
-            '';
+          src = pkgs.fetchgit {
+            url = "https://github.com/celestiaorg/celestia-node";
+            rev = "05238b3e087eb9ecd3b9684cd0125f2400f6f0c7";
+            hash = "sha256-bmFcJrC4ocbCw1pew2HKEdLj6+1D/0VuWtdoTs1S2sU=";
           };
 
-          # Development Shell
-          devShells.default = mkShell {
-
-            ROCKSDB=pkgs.rocksdb;
-            
-            # for linux set SNAPPY variable
-            SNAPPY = if stdenv.isLinux then pkgs.snappy else null;
-
+          vendorHash = "sha256-8RC/9KiFOsEJDpt7d8WtzRLn0HzYrZ1LIHo6lOKSQxU=";
+          subPackages = [ "cmd/celestia" "cmd/cel-key" ];
+        };
+    
+      in {
+        packages = {
+          inherit aptos-faucet-service celestia-app celestia-node;
+        };
+        devShells = rec {
+          default = docker-build;
+          docker-build = pkgs.mkShell {
+            ROCKSDB = pkgs.rocksdb;
+            SNAPPY = if pkgs.stdenv.isLinux then pkgs.snappy else null;
             OPENSSL_DEV = pkgs.openssl.dev;
-            PKG_CONFIG_PATH = "${pkgs.openssl.dev}/lib/pkgconfig";
             MONZA_APTOS_PATH = monza-aptos;
-
-            buildInputs = [] ++buildDependencies ++sysDependencies ++testDependencies;
-            nativeBuildInputs = [] ++buildDependencies ++sysDependencies;
+         
+            buildInputs = with pkgs; [
+              # rust toolchain
+              (toolchain pkgs)
+
+              # build dependencies
+              llvmPackages.bintools openssl openssl.dev libiconv pkg-config
+              libclang.lib libz clang pkg-config protobuf rustPlatform.bindgenHook
+              lld mold coreutils postgresql
+
+              # test dependencies
+              python311 poetry just foundry-bin process-compose jq docker solc
+              grpcurl grpcui
+
+              monza-aptos
+              celestia-app celestia-node
+            ] ++ lib.optionals stdenv.isDarwin (with pkgs.darwin.apple_sdk.frameworks; [
+              Security CoreServices SystemConfiguration AppKit
+            ]) ++ lib.optionals stdenv.isLinux (with pkgs; [
+              udev systemd snappy bzip2 elfutils.dev
+            ]);
+
+            LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib/";
 
             shellHook = ''
-              #!/bin/bash -e
+              #!/usr/bin/env ${pkgs.bash}
 
-              // # Movement Swap Core
-              DOT_MOVEMENT_PATH=$(pwd)/.movement
+              DOT_MOVEMENT_PATH=$(pwd).movement
               mkdir -p $DOT_MOVEMENT_PATH
 
+              # export PKG_CONFIG_PATH=$PKG_CONFIG_PATH_FOR_TARGET
+
               echo "Monza Aptos path: $MONZA_APTOS_PATH"
               cat <<'EOF'
                  _  _   __   _  _  ____  _  _  ____  __ _  ____
@@ -198,8 +133,7 @@
               echo "Develop with Move Anywhere"
             '';
           };
-        }
+        };
+      }
     );
 }
-
-
```

### networks/suzuka/indexer/Cargo.toml
```diff
@@ -9,6 +9,10 @@ homepage = { workspace = true }
 publish = { workspace = true }
 rust-version = { workspace = true }
 
+[[bin]]
+name = "load_metadata"
+path = "bin/load_metadata.rs"
+
 [dependencies]
 anyhow = { workspace = true }
 tokio = { workspace = true }
@@ -20,7 +24,8 @@ tracing = { workspace = true }
 tracing-subscriber = { workspace = true }
 maptos-execution-util = { workspace = true }
 clap = { workspace = true }
-reqwest = { workspace = true }
+reqwest = { workspace = true, features = ["json"] }
+serde_json = { workspace = true }
 tempfile = { workspace = true }
 
 [lints]
```

### networks/suzuka/indexer/bin/load_metadata.rs
```diff
@@ -0,0 +1,104 @@
+use anyhow::{anyhow, Context, Result};
+use reqwest::Url;
+use tracing::info;
+
+const HASURA_METADATA: &str = include_str!("../hasura_metadata.json");
+
+#[tokio::main]
+async fn main() -> Result<(), anyhow::Error> {
+	let indexer_api_url =
+		std::env::var("INDEXER_API_URL").unwrap_or("http://127.0.0.1:8085".to_string());
+
+	// Replace the postgres connection definition in the metadata file
+	// with the provided in the env var INDEXER_V2_POSTGRES_URL
+	let postgres_host = std::env::var("POSTGRES_DB_HOST").unwrap_or("postgres".to_string());
+	let postgres_url = format!("postgres://postgres:password@{postgres_host}:5432/postgres");
+	let metadata_file = HASURA_METADATA.replace("INDEXER_V2_POSTGRES_URL", &postgres_url);
+
+	post_metadata(indexer_api_url.parse()?, &metadata_file)
+		.await
+		.context("Failed to apply Hasura metadata for Indexer API")?;
+
+	Ok(())
+}
+
+/// This submits a POST request to apply metadata to a Hasura API.
+async fn post_metadata(url: Url, metadata_content: &str) -> Result<()> {
+	// Parse the metadata content as JSON.
+	let metadata_json: serde_json::Value = serde_json::from_str(metadata_content)?;
+
+	// Make the request.
+	info!("Submitting request to apply Hasura metadata");
+	let response =
+		make_hasura_metadata_request(url, "replace_metadata", Some(metadata_json)).await?;
+	info!("Received response for applying Hasura metadata: {:?}", response);
+
+	// Confirm that the metadata was applied successfully and there is no inconsistency
+	// between the schema and the underlying DB schema.
+	if let Some(obj) = response.as_object() {
+		if let Some(is_consistent_val) = obj.get("is_consistent") {
+			if is_consistent_val.as_bool() == Some(true) {
+				return Ok(());
+			}
+		}
+	}
+
+	Err(anyhow!(
+        "Something went wrong applying the Hasura metadata, perhaps it is not consistent with the DB. Response: {:#?}",
+        response
+    ))
+}
+
+/// This confirms that the metadata has been applied. We use this in the health
+/// checker.
+pub async fn confirm_metadata_applied(url: Url) -> Result<()> {
+	// Make the request.
+	info!("Confirming Hasura metadata applied...");
+	let response = make_hasura_metadata_request(url, "export_metadata", None).await?;
+	info!("Received response for confirming Hasura metadata applied: {:?}", response);
+
+	// If the sources field is set it means the metadata was applied successfully.
+	if let Some(obj) = response.as_object() {
+		if let Some(sources) = obj.get("sources") {
+			if let Some(sources) = sources.as_array() {
+				if !sources.is_empty() {
+					return Ok(());
+				}
+			}
+		}
+	}
+
+	Err(anyhow!("The Hasura metadata has not been applied yet. Response: {:#?}", response))
+}
+
+/// The /v1/metadata endpoint supports a few different operations based on the `type`
+/// field in the request body. All requests have a similar format, with these `type`
+/// and `args` fields.
+async fn make_hasura_metadata_request(
+	mut url: Url,
+	typ: &str,
+	args: Option<serde_json::Value>,
+) -> Result<serde_json::Value> {
+	let client = reqwest::Client::new();
+
+	// Update the query path.
+	url.set_path("/v1/metadata");
+
+	// Construct the payload.
+	let mut payload = serde_json::Map::new();
+	payload.insert("type".to_string(), serde_json::Value::String(typ.to_string()));
+
+	// If args is provided, use that. Otherwise use an empty object. We have to set it
+	// no matter what because the API expects the args key to be set.
+	let args = match args {
+		Some(args) => args,
+		None => serde_json::Value::Object(serde_json::Map::new()),
+	};
+	payload.insert("args".to_string(), args);
+
+	// Send the POST request.
+	let response = client.post(url).json(&payload).send().await?;
+
+	// Return the response as a JSON value.
+	response.json().await.context("Failed to parse response as JSON")
+}
```

### networks/suzuka/indexer/hasura_metadata.json
```diff
@@ -0,0 +1,2239 @@
+{
+  "resource_version": 319,
+  "metadata": {
+    "version": 3,
+    "sources": [
+      {
+        "name": "indexer-v2",
+        "kind": "postgres",
+        "tables": [
+          {
+            "table": {
+              "name": "parsed_asset_uris",
+              "schema": "nft_metadata_crawler"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "animation_optimizer_retry_count",
+                    "asset_uri",
+                    "cdn_animation_uri",
+                    "cdn_image_uri",
+                    "cdn_json_uri",
+                    "image_optimizer_retry_count",
+                    "json_parser_retry_count",
+                    "raw_animation_uri",
+                    "raw_image_uri"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "account_transactions",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "user_transaction",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "user_transactions",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "array_relationships": [
+              {
+                "name": "coin_activities",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "coin_activities",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "delegated_staking_activities",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "delegated_staking_activities",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "fungible_asset_activities",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "fungible_asset_activities",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "token_activities",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "token_activities",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "token_activities_v2",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "token_activities_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": ["account_address", "transaction_version"],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "address_events_summary",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "block_metadata",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "min_block_height": "block_height"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "block_metadata_transactions",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "min_block_height",
+                    "num_distinct_versions",
+                    "account_address"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "address_version_from_events",
+              "schema": "public"
+            },
+            "array_relationships": [
+              {
+                "name": "coin_activities",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "coin_activities",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "delegated_staking_activities",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "delegated_staking_activities",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "token_activities",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "token_activities",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "token_activities_v2",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "token_activities_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": ["account_address", "transaction_version"],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "address_version_from_move_resources",
+              "schema": "public"
+            },
+            "array_relationships": [
+              {
+                "name": "coin_activities",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "coin_activities",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "delegated_staking_activities",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "delegated_staking_activities",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "token_activities",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "token_activities",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "token_activities_v2",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "transaction_version": "transaction_version"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "token_activities_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": ["address", "transaction_version"],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "block_metadata_transactions",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "block_height",
+                    "epoch",
+                    "failed_proposer_indices",
+                    "id",
+                    "previous_block_votes_bitvec",
+                    "proposer",
+                    "round",
+                    "timestamp",
+                    "version"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "coin_activities",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "coin_info",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "coin_type": "coin_type"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "coin_infos",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "array_relationships": [
+              {
+                "name": "aptos_names",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "owner_address": "registered_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_aptos_names",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "activity_type",
+                    "amount",
+                    "block_height",
+                    "coin_type",
+                    "entry_function_id_str",
+                    "event_account_address",
+                    "event_creation_number",
+                    "event_index",
+                    "event_sequence_number",
+                    "is_gas_fee",
+                    "is_transaction_success",
+                    "owner_address",
+                    "storage_refund_amount",
+                    "transaction_timestamp",
+                    "transaction_version"
+                  ],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "coin_balances",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "amount",
+                    "coin_type",
+                    "coin_type_hash",
+                    "owner_address",
+                    "transaction_timestamp",
+                    "transaction_version"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "coin_infos",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "coin_type",
+                    "coin_type_hash",
+                    "creator_address",
+                    "decimals",
+                    "name",
+                    "supply_aggregator_table_handle",
+                    "supply_aggregator_table_key",
+                    "symbol",
+                    "transaction_created_timestamp",
+                    "transaction_version_created"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "coin_supply",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "coin_type",
+                    "coin_type_hash",
+                    "supply",
+                    "transaction_epoch",
+                    "transaction_timestamp",
+                    "transaction_version"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "collection_datas",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "collection_data_id_hash",
+                    "collection_name",
+                    "creator_address",
+                    "description",
+                    "description_mutable",
+                    "maximum",
+                    "maximum_mutable",
+                    "metadata_uri",
+                    "supply",
+                    "table_handle",
+                    "transaction_timestamp",
+                    "transaction_version",
+                    "uri_mutable"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_ans_lookup",
+              "schema": "public"
+            },
+            "array_relationships": [
+              {
+                "name": "all_token_ownerships",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_name": "name"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_token_ownerships",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "domain",
+                    "expiration_timestamp",
+                    "is_deleted",
+                    "last_transaction_version",
+                    "registered_address",
+                    "subdomain",
+                    "token_name"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_ans_lookup_v2",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "domain",
+                    "expiration_timestamp",
+                    "is_deleted",
+                    "last_transaction_version",
+                    "registered_address",
+                    "subdomain",
+                    "token_name",
+                    "token_standard"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                },
+                "comment": ""
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_aptos_names",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "is_domain_owner",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "domain_with_suffix": "token_name",
+                      "owner_address": "owner_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_aptos_names",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "domain",
+                    "domain_expiration_timestamp",
+                    "domain_with_suffix",
+                    "expiration_timestamp",
+                    "is_active",
+                    "is_primary",
+                    "last_transaction_version",
+                    "owner_address",
+                    "registered_address",
+                    "subdomain",
+                    "subdomain_expiration_policy",
+                    "token_name",
+                    "token_standard"
+                  ],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                },
+                "comment": ""
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_coin_balances",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "coin_info",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "coin_type_hash": "coin_type_hash"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "coin_infos",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "amount",
+                    "coin_type",
+                    "coin_type_hash",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "owner_address"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_collection_datas",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "collection_data_id_hash",
+                    "collection_name",
+                    "creator_address",
+                    "description",
+                    "description_mutable",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "maximum",
+                    "maximum_mutable",
+                    "metadata_uri",
+                    "supply",
+                    "table_handle",
+                    "uri_mutable"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_collection_ownership_v2_view",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "current_collection",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "collection_id": "collection_id"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_collections_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "distinct_tokens",
+                    "last_transaction_version",
+                    "collection_id",
+                    "collection_name",
+                    "creator_address",
+                    "owner_address",
+                    "collection_uri",
+                    "single_token_uri"
+                  ],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_collections_v2",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "cdn_asset_uris",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "uri": "asset_uri"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "parsed_asset_uris",
+                      "schema": "nft_metadata_crawler"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "collection_id",
+                    "collection_name",
+                    "creator_address",
+                    "current_supply",
+                    "description",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "max_supply",
+                    "mutable_description",
+                    "mutable_uri",
+                    "table_handle_v1",
+                    "token_standard",
+                    "total_minted_v2",
+                    "uri"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_delegated_staking_pool_balances",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "active_table_handle",
+                    "inactive_table_handle",
+                    "last_transaction_version",
+                    "operator_commission_percentage",
+                    "staking_pool_address",
+                    "total_coins",
+                    "total_shares"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_delegated_voter",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "delegation_pool_address",
+                    "delegator_address",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "pending_voter",
+                    "table_handle",
+                    "voter"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                },
+                "comment": ""
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_delegator_balances",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "current_pool_balance",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "pool_address": "staking_pool_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_delegated_staking_pool_balances",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "staking_pool_metadata",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "pool_address": "staking_pool_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_staking_pool_voter",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "delegator_address",
+                    "last_transaction_version",
+                    "parent_table_handle",
+                    "pool_address",
+                    "pool_type",
+                    "shares",
+                    "table_handle"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_fungible_asset_balances",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "metadata",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "asset_type": "asset_type"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "fungible_asset_metadata",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "amount",
+                    "asset_type",
+                    "is_frozen",
+                    "is_primary",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "owner_address",
+                    "storage_id",
+                    "token_standard"
+                  ],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_objects",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "allow_ungated_transfer",
+                    "is_deleted",
+                    "last_guid_creation_num",
+                    "last_transaction_version",
+                    "object_address",
+                    "owner_address",
+                    "state_key_hash"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_staking_pool_voter",
+              "schema": "public"
+            },
+            "array_relationships": [
+              {
+                "name": "operator_aptos_name",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "operator_address": "registered_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_aptos_names",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "last_transaction_version",
+                    "operator_address",
+                    "staking_pool_address",
+                    "voter_address"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_table_items",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "decoded_key",
+                    "decoded_value",
+                    "is_deleted",
+                    "key",
+                    "key_hash",
+                    "last_transaction_version",
+                    "table_handle"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_token_datas",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "current_collection_data",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "collection_data_id_hash": "collection_data_id_hash"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_collection_datas",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "collection_data_id_hash",
+                    "collection_name",
+                    "creator_address",
+                    "default_properties",
+                    "description",
+                    "description_mutable",
+                    "largest_property_version",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "maximum",
+                    "maximum_mutable",
+                    "metadata_uri",
+                    "name",
+                    "payee_address",
+                    "properties_mutable",
+                    "royalty_mutable",
+                    "royalty_points_denominator",
+                    "royalty_points_numerator",
+                    "supply",
+                    "token_data_id_hash",
+                    "uri_mutable"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_token_datas_v2",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "aptos_name",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_name": "token_name"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_aptos_names",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "cdn_asset_uris",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_uri": "asset_uri"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "parsed_asset_uris",
+                      "schema": "nft_metadata_crawler"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "current_collection",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "collection_id": "collection_id"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_collections_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "array_relationships": [
+              {
+                "name": "current_token_ownerships",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_data_id": "token_data_id"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_token_ownerships_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "collection_id",
+                    "decimals",
+                    "description",
+                    "is_deleted_v2",
+                    "is_fungible_v2",
+                    "largest_property_version_v1",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "maximum",
+                    "supply",
+                    "token_data_id",
+                    "token_name",
+                    "token_properties",
+                    "token_standard",
+                    "token_uri"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_token_ownerships",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "aptos_name",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "name": "token_name"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_aptos_names",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "current_collection_data",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "collection_data_id_hash": "collection_data_id_hash"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_collection_datas",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "current_token_data",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_data_id_hash": "token_data_id_hash"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_token_datas",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "amount",
+                    "collection_data_id_hash",
+                    "collection_name",
+                    "creator_address",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "name",
+                    "owner_address",
+                    "property_version",
+                    "table_type",
+                    "token_data_id_hash",
+                    "token_properties"
+                  ],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_token_ownerships_v2",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "current_token_data",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_data_id": "token_data_id"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_token_datas_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "array_relationships": [
+              {
+                "name": "composed_nfts",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_data_id": "owner_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_token_ownerships_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "amount",
+                    "is_fungible_v2",
+                    "is_soulbound_v2",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "non_transferrable_by_owner",
+                    "owner_address",
+                    "property_version_v1",
+                    "storage_id",
+                    "table_type_v1",
+                    "token_data_id",
+                    "token_properties_mutated_v1",
+                    "token_standard"
+                  ],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "current_token_pending_claims",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "current_collection_data",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "collection_data_id_hash": "collection_data_id_hash"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_collection_datas",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "current_collection_v2",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "collection_id": "collection_id"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_collections_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "current_token_data",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_data_id_hash": "token_data_id_hash"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_token_datas",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "current_token_data_v2",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_data_id": "token_data_id"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_token_datas_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "token",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "last_transaction_version": "transaction_version",
+                      "property_version": "property_version",
+                      "token_data_id_hash": "token_data_id_hash"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "tokens",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "amount",
+                    "collection_data_id_hash",
+                    "collection_id",
+                    "collection_name",
+                    "creator_address",
+                    "from_address",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "name",
+                    "property_version",
+                    "table_handle",
+                    "to_address",
+                    "token_data_id",
+                    "token_data_id_hash"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "delegated_staking_activities",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "amount",
+                    "delegator_address",
+                    "event_index",
+                    "event_type",
+                    "pool_address",
+                    "transaction_version"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "delegated_staking_pool_balances",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "active_table_handle",
+                    "inactive_table_handle",
+                    "operator_commission_percentage",
+                    "staking_pool_address",
+                    "total_coins",
+                    "total_shares",
+                    "transaction_version"
+                  ],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                },
+                "comment": ""
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "delegated_staking_pools",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "current_staking_pool",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "staking_pool_address": "staking_pool_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_staking_pool_voter",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "first_transaction_version",
+                    "staking_pool_address"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "delegator_distinct_pool",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "current_pool_balance",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "pool_address": "staking_pool_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_delegated_staking_pool_balances",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "staking_pool_metadata",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "pool_address": "staking_pool_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_staking_pool_voter",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": ["delegator_address", "pool_address"],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "events",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "account_address",
+                    "creation_number",
+                    "data",
+                    "event_index",
+                    "sequence_number",
+                    "transaction_block_height",
+                    "transaction_version",
+                    "type",
+                    "indexed_type"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "fungible_asset_activities",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "metadata",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "asset_type": "asset_type"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "fungible_asset_metadata",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "array_relationships": [
+              {
+                "name": "owner_aptos_names",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "owner_address": "registered_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_aptos_names",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "amount",
+                    "asset_type",
+                    "block_height",
+                    "entry_function_id_str",
+                    "event_index",
+                    "gas_fee_payer_address",
+                    "is_frozen",
+                    "is_gas_fee",
+                    "is_transaction_success",
+                    "owner_address",
+                    "storage_id",
+                    "storage_refund_amount",
+                    "token_standard",
+                    "transaction_timestamp",
+                    "transaction_version",
+                    "type"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "fungible_asset_metadata",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "asset_type",
+                    "creator_address",
+                    "decimals",
+                    "icon_uri",
+                    "last_transaction_timestamp",
+                    "last_transaction_version",
+                    "maximum_v2",
+                    "name",
+                    "project_uri",
+                    "supply_aggregator_table_handle_v1",
+                    "supply_aggregator_table_key_v1",
+                    "supply_v2",
+                    "symbol",
+                    "token_standard"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "indexer_status",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": ["db", "is_indexer_up"],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "ledger_infos",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": ["chain_id"],
+                  "filter": {}
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "move_resources",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": ["address", "transaction_version"],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "num_active_delegator_per_pool",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": ["num_active_delegator", "pool_address"],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "processor_status",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "last_success_version",
+                    "last_transaction_timestamp",
+                    "last_updated",
+                    "processor"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "proposal_votes",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "num_votes",
+                    "proposal_id",
+                    "should_pass",
+                    "staking_pool_address",
+                    "transaction_timestamp",
+                    "transaction_version",
+                    "voter_address"
+                  ],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "signatures",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "is_sender_primary",
+                    "multi_agent_index",
+                    "multi_sig_index",
+                    "public_key",
+                    "public_key_indices",
+                    "signature",
+                    "signer",
+                    "threshold",
+                    "transaction_block_height",
+                    "transaction_version",
+                    "type"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                },
+                "comment": ""
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "table_items",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "decoded_key",
+                    "decoded_value",
+                    "key",
+                    "table_handle",
+                    "transaction_version",
+                    "write_set_change_index"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "table_metadatas",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": ["handle", "key_type", "value_type"],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "token_activities",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "current_token_data",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_data_id_hash": "token_data_id_hash"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_token_datas",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "array_relationships": [
+              {
+                "name": "aptos_names_owner",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "event_account_address": "registered_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_aptos_names",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "aptos_names_to",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "to_address": "registered_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_aptos_names",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "coin_amount",
+                    "coin_type",
+                    "collection_data_id_hash",
+                    "collection_name",
+                    "creator_address",
+                    "event_account_address",
+                    "event_creation_number",
+                    "event_index",
+                    "event_sequence_number",
+                    "from_address",
+                    "name",
+                    "property_version",
+                    "to_address",
+                    "token_amount",
+                    "token_data_id_hash",
+                    "transaction_timestamp",
+                    "transaction_version",
+                    "transfer_type"
+                  ],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "token_activities_v2",
+              "schema": "public"
+            },
+            "object_relationships": [
+              {
+                "name": "current_token_data",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "token_data_id": "token_data_id"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_token_datas_v2",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "array_relationships": [
+              {
+                "name": "aptos_names_from",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "from_address": "registered_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_aptos_names",
+                      "schema": "public"
+                    }
+                  }
+                }
+              },
+              {
+                "name": "aptos_names_to",
+                "using": {
+                  "manual_configuration": {
+                    "column_mapping": {
+                      "to_address": "registered_address"
+                    },
+                    "insertion_order": null,
+                    "remote_table": {
+                      "name": "current_aptos_names",
+                      "schema": "public"
+                    }
+                  }
+                }
+              }
+            ],
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "after_value",
+                    "before_value",
+                    "entry_function_id_str",
+                    "event_account_address",
+                    "event_index",
+                    "from_address",
+                    "is_fungible_v2",
+                    "property_version_v1",
+                    "to_address",
+                    "token_amount",
+                    "token_data_id",
+                    "token_standard",
+                    "transaction_timestamp",
+                    "transaction_version",
+                    "type"
+                  ],
+                  "filter": {},
+                  "limit": 100,
+                  "allow_aggregations": true
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "token_datas",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "collection_data_id_hash",
+                    "collection_name",
+                    "creator_address",
+                    "default_properties",
+                    "description",
+                    "description_mutable",
+                    "largest_property_version",
+                    "maximum",
+                    "maximum_mutable",
+                    "metadata_uri",
+                    "name",
+                    "payee_address",
+                    "properties_mutable",
+                    "royalty_mutable",
+                    "royalty_points_denominator",
+                    "royalty_points_numerator",
+                    "supply",
+                    "token_data_id_hash",
+                    "transaction_timestamp",
+                    "transaction_version",
+                    "uri_mutable"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "token_ownerships",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "amount",
+                    "collection_data_id_hash",
+                    "collection_name",
+                    "creator_address",
+                    "name",
+                    "owner_address",
+                    "property_version",
+                    "table_handle",
+                    "table_type",
+                    "token_data_id_hash",
+                    "transaction_timestamp",
+                    "transaction_version"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "tokens",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "collection_data_id_hash",
+                    "collection_name",
+                    "creator_address",
+                    "name",
+                    "property_version",
+                    "token_data_id_hash",
+                    "token_properties",
+                    "transaction_timestamp",
+                    "transaction_version"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          },
+          {
+            "table": {
+              "name": "user_transactions",
+              "schema": "public"
+            },
+            "select_permissions": [
+              {
+                "role": "anonymous",
+                "permission": {
+                  "columns": [
+                    "block_height",
+                    "entry_function_id_str",
+                    "epoch",
+                    "expiration_timestamp_secs",
+                    "gas_unit_price",
+                    "max_gas_amount",
+                    "parent_signature_type",
+                    "sender",
+                    "sequence_number",
+                    "timestamp",
+                    "version"
+                  ],
+                  "filter": {},
+                  "limit": 100
+                }
+              }
+            ]
+          }
+        ],
+        "configuration": {
+          "connection_info": {
+            "database_url": "INDEXER_V2_POSTGRES_URL",
+            "isolation_level": "read-committed",
+            "use_prepared_statements": false
+          }
+        }
+      }
+    ],
+    "query_collections": [
+      {
+        "name": "allowed-queries",
+        "definition": {
+          "queries": [
+            {
+              "name": "Latest Processor Status",
+              "query": "query LatestProcessorStatus {\n  processor_status {\n    processor\n    last_updated\n    last_success_version\n    last_transaction_timestamp\n  }\n}"
+            }
+          ]
+        }
+      }
+    ],
+    "allowlist": [
+      {
+        "collection": "allowed-queries",
+        "scope": {
+          "global": true
+        }
+      }
+    ],
+    "rest_endpoints": [
+      {
+        "comment": "",
+        "definition": {
+          "query": {
+            "collection_name": "allowed-queries",
+            "query_name": "Latest Processor Status"
+          }
+        },
+        "methods": ["GET"],
+        "name": "Latest Processor Status",
+        "url": "get_latest_processor_status"
+      }
+    ],
+    "api_limits": {
+      "depth_limit": {
+        "global": 5,
+        "per_role": {}
+      },
+      "disabled": false,
+      "time_limit": {
+        "global": 10,
+        "per_role": {}
+      }
+    },
+    "metrics_config": {
+      "analyze_query_variables": true,
+      "analyze_response_body": true
+    }
+  }
+}
```
