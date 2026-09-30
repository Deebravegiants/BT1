# [?] Merge pull request #576 from movementlabsxyz/mikhail/fix-indexer-runtime-crash

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-09-20
Source: https://github.com/movement-network/movement/commit/a3b862d38ccc1d4770211df2e60f6f769e340445
Type: security-commit

## Details
Merge pull request #576 from movementlabsxyz/mikhail/fix-indexer-runtime-crash

Fix test crashes on dropping indexer runtime

## Patch
### .github/workflows/checks-all.yml
```diff
@@ -12,7 +12,7 @@ on:
 
 jobs:
  
-  cargo-check:
+  build:
     strategy:
       matrix:
         include:
@@ -40,9 +40,36 @@ jobs:
     - name: Run Cargo Check in nix environment
       run: |
         nix develop --command bash  -c "cargo check --all-targets"  
-        nix develop --command bash  -c "cargo test -p memseq"  
-        nix develop --command bash  -c "cargo test -p move-rocks"
-        nix develop --command bash  -c "cargo test -p movement-types"    
+
+  unit-tests:
+    strategy:
+      matrix:
+        include:
+          - os: ubuntu-22.04
+            arch: x86_64
+            runs-on: buildjet-8vcpu-ubuntu-2204
+          - os: macos-13-latest
+            arch: arm64
+            runs-on: macos-13-xlarge
+
+    runs-on: ${{ matrix.runs-on }}
+
+    steps:
+    - name: Checkout repository
+      uses: actions/checkout@v4
+
+    - name: Install Nix
+      uses: DeterminateSystems/nix-installer-action@main
+
+    - name: Run unit tests in nix environment
+      run: |
+        nix develop --command bash <<EOF
+          cargo test \
+            -p maptos-opt-executor \
+            -p memseq \
+            -p move-rocks \
+            -p movement-types
+        EOF
 
   suzuka-full-node-local:
     if: github.event.label.name == 'cicd:suzuka-full-node' ||  github.ref == 'refs/heads/main'
@@ -129,8 +156,8 @@ jobs:
     - name: Run Suzuka Full Node Tests Against Holesky and Local Celestia
       env: 
         CELESTIA_LOG_LEVEL: FATAL # adjust the log level while debugging
+        MCR_DEPLOYMENT_ACCOUNT_PRIVATE_KEY: ${{ secrets.MCR_DEPLOYMENT_ACCOUNT_PRIVATE_KEY }}
       run: |
-        export MCR_DEPLOYMENT_ACCOUNT_PRIVATE_KEY=${{ secrets.MCR_DEPLOYMENT_ACCOUNT_PRIVATE_KEY }}
         nix develop --command bash  -c "just suzuka-full-node native build.setup.eth-holesky.celestia-local.test -t=false"
         nix develop --command bash  -c "just suzuka-full-node native build.setup.eth-holesky.celestia-local.test -t=false"
 
```

### Cargo.lock
```diff
@@ -11,7 +11,7 @@ checksum = "fe438c63458706e03479442743baae6c88256498e6431708f6dfc520a26515d3"
 [[package]]
 name = "abstract-domain-derive"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -800,7 +800,7 @@ checksum = "10f00e1f6e58a40e807377c75c6a7f97bf9044fab57816f2414e6f5f4499d7b8"
 [[package]]
 name = "aptos-abstract-gas-usage"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-gas-algebra",
@@ -813,7 +813,7 @@ dependencies = [
 [[package]]
 name = "aptos-accumulator"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-crypto",
@@ -823,7 +823,7 @@ dependencies = [
 [[package]]
 name = "aptos-aggregator"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-logger",
  "aptos-types",
@@ -837,7 +837,7 @@ dependencies = [
 [[package]]
 name = "aptos-api"
 version = "0.2.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-api-types",
@@ -879,7 +879,7 @@ dependencies = [
 [[package]]
 name = "aptos-api-types"
 version = "0.0.1"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-config",
@@ -909,7 +909,7 @@ dependencies = [
 [[package]]
 name = "aptos-bcs-utils"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "hex",
@@ -918,7 +918,7 @@ dependencies = [
 [[package]]
 name = "aptos-bitvec"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "serde",
  "serde_bytes",
@@ -927,7 +927,7 @@ dependencies = [
 [[package]]
 name = "aptos-block-executor"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-aggregator",
@@ -962,7 +962,7 @@ dependencies = [
 [[package]]
 name = "aptos-block-partitioner"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-crypto",
  "aptos-logger",
@@ -983,7 +983,7 @@ dependencies = [
 [[package]]
 name = "aptos-bounded-executor"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "futures",
  "rustversion",
@@ -993,15 +993,15 @@ dependencies = [
 [[package]]
 name = "aptos-build-info"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "shadow-rs",
 ]
 
 [[package]]
 name = "aptos-cached-packages"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-framework",
@@ -1015,7 +1015,7 @@ dependencies = [
 [[package]]
 name = "aptos-channels"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-infallible",
@@ -1026,7 +1026,7 @@ dependencies = [
 [[package]]
 name = "aptos-compression"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-logger",
  "aptos-metrics-core",
@@ -1038,7 +1038,7 @@ dependencies = [
 [[package]]
 name = "aptos-config"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-crypto",
@@ -1069,7 +1069,7 @@ dependencies = [
 [[package]]
 name = "aptos-consensus-types"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-bitvec",
@@ -1096,7 +1096,7 @@ dependencies = [
 [[package]]
 name = "aptos-crypto"
 version = "0.0.3"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aes-gcm",
  "anyhow",
@@ -1149,7 +1149,7 @@ dependencies = [
 [[package]]
 name = "aptos-crypto-derive"
 version = "0.0.3"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -1159,7 +1159,7 @@ dependencies = [
 [[package]]
 name = "aptos-db"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-accumulator",
@@ -1206,7 +1206,7 @@ dependencies = [
 [[package]]
 name = "aptos-db-indexer"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-config",
@@ -1226,7 +1226,7 @@ dependencies = [
 [[package]]
 name = "aptos-db-indexer-schemas"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-schemadb",
@@ -1240,7 +1240,7 @@ dependencies = [
 [[package]]
 name = "aptos-dkg"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-crypto",
@@ -1271,7 +1271,7 @@ dependencies = [
 [[package]]
 name = "aptos-drop-helper"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-infallible",
  "aptos-metrics-core",
@@ -1282,7 +1282,7 @@ dependencies = [
 [[package]]
 name = "aptos-event-notifications"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-channels",
@@ -1298,7 +1298,7 @@ dependencies = [
 [[package]]
 name = "aptos-executor"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-consensus-types",
@@ -1330,7 +1330,7 @@ dependencies = [
 [[package]]
 name = "aptos-executor-service"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-block-partitioner",
  "aptos-config",
@@ -1360,7 +1360,7 @@ dependencies = [
 [[package]]
 name = "aptos-executor-test-helpers"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-cached-packages",
@@ -1382,7 +1382,7 @@ dependencies = [
 [[package]]
 name = "aptos-executor-types"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-crypto",
@@ -1402,7 +1402,7 @@ dependencies = [
 [[package]]
 name = "aptos-experimental-runtimes"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-runtimes",
  "core_affinity",
@@ -1415,7 +1415,7 @@ dependencies = [
 [[package]]
 name = "aptos-faucet-core"
 version = "2.0.1"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-config",
@@ -1449,7 +1449,7 @@ dependencies = [
 [[package]]
 name = "aptos-faucet-metrics-server"
 version = "2.0.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-logger",
@@ -1463,7 +1463,7 @@ dependencies = [
 [[package]]
 name = "aptos-framework"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-aggregator",
@@ -1531,7 +1531,7 @@ dependencies = [
 [[package]]
 name = "aptos-gas-algebra"
 version = "0.0.1"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "either",
  "move-core-types",
@@ -1540,7 +1540,7 @@ dependencies = [
 [[package]]
 name = "aptos-gas-meter"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-gas-algebra",
  "aptos-gas-schedule",
@@ -1555,7 +1555,7 @@ dependencies = [
 [[package]]
 name = "aptos-gas-profiling"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-gas-algebra",
@@ -1575,7 +1575,7 @@ dependencies = [
 [[package]]
 name = "aptos-gas-schedule"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-gas-algebra",
  "aptos-global-constants",
@@ -1588,17 +1588,17 @@ dependencies = [
 [[package]]
 name = "aptos-global-constants"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 
 [[package]]
 name = "aptos-id-generator"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 
 [[package]]
 name = "aptos-indexer"
 version = "0.0.1"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-api",
@@ -1630,7 +1630,7 @@ dependencies = [
 [[package]]
 name = "aptos-indexer-grpc-fullnode"
 version = "1.0.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-api",
@@ -1642,7 +1642,7 @@ dependencies = [
  "aptos-mempool",
  "aptos-metrics-core",
  "aptos-moving-average 0.1.0 (git+https://github.com/movementlabsxyz/aptos-indexer-processors)",
- "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b)",
+ "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899)",
  "aptos-runtimes",
  "aptos-storage-interface",
  "aptos-types",
@@ -1668,7 +1668,7 @@ dependencies = [
 [[package]]
 name = "aptos-indexer-grpc-table-info"
 version = "1.0.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-api",
@@ -1699,11 +1699,11 @@ dependencies = [
 [[package]]
 name = "aptos-indexer-grpc-utils"
 version = "1.0.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-metrics-core",
- "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b)",
+ "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899)",
  "async-trait",
  "backoff",
  "base64 0.13.1",
@@ -1731,12 +1731,12 @@ dependencies = [
 [[package]]
 name = "aptos-infallible"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 
 [[package]]
 name = "aptos-jellyfish-merkle"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-crypto",
@@ -1764,7 +1764,7 @@ dependencies = [
 [[package]]
 name = "aptos-keygen"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-crypto",
  "aptos-types",
@@ -1774,7 +1774,7 @@ dependencies = [
 [[package]]
 name = "aptos-language-e2e-tests"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-abstract-gas-usage",
@@ -1818,7 +1818,7 @@ dependencies = [
 [[package]]
 name = "aptos-ledger"
 version = "0.2.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-crypto",
  "aptos-types",
@@ -1831,7 +1831,7 @@ dependencies = [
 [[package]]
 name = "aptos-log-derive"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -1841,7 +1841,7 @@ dependencies = [
 [[package]]
 name = "aptos-logger"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-infallible",
  "aptos-log-derive",
@@ -1865,7 +1865,7 @@ dependencies = [
 [[package]]
 name = "aptos-memory-usage-tracker"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-gas-algebra",
  "aptos-gas-meter",
@@ -1878,7 +1878,7 @@ dependencies = [
 [[package]]
 name = "aptos-mempool"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-bounded-executor",
@@ -1918,7 +1918,7 @@ dependencies = [
 [[package]]
 name = "aptos-mempool-notifications"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-types",
  "async-trait",
@@ -1931,7 +1931,7 @@ dependencies = [
 [[package]]
 name = "aptos-memsocket"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-infallible",
  "bytes 1.7.1",
@@ -1942,7 +1942,7 @@ dependencies = [
 [[package]]
 name = "aptos-metrics-core"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "prometheus",
@@ -1951,7 +1951,7 @@ dependencies = [
 [[package]]
 name = "aptos-move-stdlib"
 version = "0.1.1"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-gas-schedule",
  "aptos-native-interface",
@@ -1966,7 +1966,7 @@ dependencies = [
 [[package]]
 name = "aptos-moving-average"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=a11a7ef5346e11a827cec7394a7a3cc4461af820#a11a7ef5346e11a827cec7394a7a3cc4461af820"
+source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58#1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58"
 dependencies = [
  "chrono",
 ]
@@ -1982,7 +1982,7 @@ dependencies = [
 [[package]]
 name = "aptos-mvhashmap"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-aggregator",
@@ -2003,7 +2003,7 @@ dependencies = [
 [[package]]
 name = "aptos-native-interface"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-gas-algebra",
  "aptos-gas-schedule",
@@ -2020,7 +2020,7 @@ dependencies = [
 [[package]]
 name = "aptos-netcore"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-memsocket",
  "aptos-proxy",
@@ -2037,7 +2037,7 @@ dependencies = [
 [[package]]
 name = "aptos-network"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-bitvec",
@@ -2082,7 +2082,7 @@ dependencies = [
 [[package]]
 name = "aptos-node-identity"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-types",
@@ -2093,7 +2093,7 @@ dependencies = [
 [[package]]
 name = "aptos-node-resource-metrics"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-build-info",
  "aptos-infallible",
@@ -2109,7 +2109,7 @@ dependencies = [
 [[package]]
 name = "aptos-num-variants"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -2119,7 +2119,7 @@ dependencies = [
 [[package]]
 name = "aptos-openapi"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "async-trait",
  "percent-encoding",
@@ -2132,7 +2132,7 @@ dependencies = [
 [[package]]
 name = "aptos-package-builder"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-framework",
@@ -2145,7 +2145,7 @@ dependencies = [
 [[package]]
 name = "aptos-peer-monitoring-service-types"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-config",
  "aptos-types",
@@ -2170,7 +2170,7 @@ dependencies = [
 [[package]]
 name = "aptos-proptest-helpers"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "crossbeam",
  "proptest",
@@ -2180,7 +2180,7 @@ dependencies = [
 [[package]]
 name = "aptos-protos"
 version = "1.3.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=338f9a1bcc06f62ce4a4994f1642b9a61b631ee0#338f9a1bcc06f62ce4a4994f1642b9a61b631ee0"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "futures-core",
  "pbjson",
@@ -2192,7 +2192,7 @@ dependencies = [
 [[package]]
 name = "aptos-protos"
 version = "1.3.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=338f9a1bcc06f62ce4a4994f1642b9a61b631ee0#338f9a1bcc06f62ce4a4994f1642b9a61b631ee0"
 dependencies = [
  "futures-core",
  "pbjson",
@@ -2204,15 +2204,15 @@ dependencies = [
 [[package]]
 name = "aptos-proxy"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "ipnet",
 ]
 
 [[package]]
 name = "aptos-push-metrics"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-logger",
  "aptos-metrics-core",
@@ -2223,7 +2223,7 @@ dependencies = [
 [[package]]
 name = "aptos-resource-viewer"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-types",
@@ -2237,7 +2237,7 @@ dependencies = [
 [[package]]
 name = "aptos-rest-client"
 version = "0.0.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-api-types",
@@ -2260,7 +2260,7 @@ dependencies = [
 [[package]]
 name = "aptos-rocksdb-options"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-config",
  "rocksdb",
@@ -2269,7 +2269,7 @@ dependencies = [
 [[package]]
 name = "aptos-runtimes"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "rayon",
  "tokio",
@@ -2278,7 +2278,7 @@ dependencies = [
 [[package]]
 name = "aptos-schemadb"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-infallible",
@@ -2295,7 +2295,7 @@ dependencies = [
 [[package]]
 name = "aptos-scratchpad"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-crypto",
  "aptos-drop-helper",
@@ -2314,7 +2314,7 @@ dependencies = [
 [[package]]
 name = "aptos-sdk"
 version = "0.0.3"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-cached-packages",
@@ -2336,7 +2336,7 @@ dependencies = [
 [[package]]
 name = "aptos-sdk-builder"
 version = "0.2.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-types",
@@ -2354,11 +2354,11 @@ dependencies = [
 [[package]]
 name = "aptos-secure-net"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-logger",
  "aptos-metrics-core",
- "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b)",
+ "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899)",
  "bcs 0.1.4",
  "crossbeam-channel",
  "once_cell",
@@ -2372,7 +2372,7 @@ dependencies = [
 [[package]]
 name = "aptos-secure-storage"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-crypto",
  "aptos-infallible",
@@ -2393,7 +2393,7 @@ dependencies = [
 [[package]]
 name = "aptos-short-hex-str"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "mirai-annotations",
  "serde",
@@ -2404,7 +2404,7 @@ dependencies = [
 [[package]]
 name = "aptos-speculative-state-helper"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-infallible",
@@ -2415,7 +2415,7 @@ dependencies = [
 [[package]]
 name = "aptos-storage-interface"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-crypto",
@@ -2463,7 +2463,7 @@ dependencies = [
 [[package]]
 name = "aptos-table-natives"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-gas-schedule",
  "aptos-native-interface",
@@ -2481,7 +2481,7 @@ dependencies = [
 [[package]]
 name = "aptos-temppath"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "hex",
  "rand 0.7.3",
@@ -2490,7 +2490,7 @@ dependencies = [
 [[package]]
 name = "aptos-time-service"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-infallible",
  "enum_dispatch",
@@ -2503,7 +2503,7 @@ dependencies = [
 [[package]]
 name = "aptos-types"
 version = "0.0.3"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-bitvec",
@@ -2560,12 +2560,12 @@ dependencies = [
 [[package]]
 name = "aptos-utils"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 
 [[package]]
 name = "aptos-vault-client"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-crypto",
  "base64 0.13.1",
@@ -2581,7 +2581,7 @@ dependencies = [
 [[package]]
 name = "aptos-vm"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-aggregator",
@@ -2631,7 +2631,7 @@ dependencies = [
 [[package]]
 name = "aptos-vm-genesis"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-cached-packages",
  "aptos-crypto",
@@ -2652,7 +2652,7 @@ dependencies = [
 [[package]]
 name = "aptos-vm-logging"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "aptos-crypto",
  "aptos-logger",
@@ -2667,7 +2667,7 @@ dependencies = [
 [[package]]
 name = "aptos-vm-types"
 version = "0.0.1"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-aggregator",
@@ -2689,7 +2689,7 @@ dependencies = [
 [[package]]
 name = "aptos-vm-validator"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "aptos-logger",
@@ -8125,7 +8125,7 @@ dependencies = [
  "aptos-language-e2e-tests",
  "aptos-logger",
  "aptos-mempool",
- "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b)",
+ "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899)",
  "aptos-sdk",
  "aptos-storage-interface",
  "aptos-temppath",
@@ -8478,7 +8478,7 @@ checksum = "1fafa6961cabd9c63bcd77a45d7e3b7f3b552b70417831fb0f56db717e72407e"
 [[package]]
 name = "move-abigen"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "bcs 0.1.4",
@@ -8495,7 +8495,7 @@ dependencies = [
 [[package]]
 name = "move-binary-format"
 version = "0.0.3"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "backtrace",
@@ -8510,12 +8510,12 @@ dependencies = [
 [[package]]
 name = "move-borrow-graph"
 version = "0.0.1"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 
 [[package]]
 name = "move-bytecode-source-map"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "bcs 0.1.4",
@@ -8530,7 +8530,7 @@ dependencies = [
 [[package]]
 name = "move-bytecode-spec"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "once_cell",
  "quote",
@@ -8540,7 +8540,7 @@ dependencies = [
 [[package]]
 name = "move-bytecode-utils"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "move-binary-format",
@@ -8552,7 +8552,7 @@ dependencies = [
 [[package]]
 name = "move-bytecode-verifier"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "fail",
  "move-binary-format",
@@ -8566,7 +8566,7 @@ dependencies = [
 [[package]]
 name = "move-bytecode-viewer"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "clap 4.5.17",
@@ -8581,7 +8581,7 @@ dependencies = [
 [[package]]
 name = "move-cli"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "clap 4.5.17",
@@ -8611,7 +8611,7 @@ dependencies = [
 [[package]]
 name = "move-command-line-common"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "difference",
@@ -8628,7 +8628,7 @@ dependencies = [
 [[package]]
 name = "move-compiler"
 version = "0.0.1"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "bcs 0.1.4",
@@ -8654,7 +8654,7 @@ dependencies = [
 [[package]]
 name = "move-compiler-v2"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "abstract-domain-derive",
  "anyhow",
@@ -8685,7 +8685,7 @@ dependencies = [
 [[package]]
 name = "move-core-types"
 version = "0.0.4"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "arbitrary",
@@ -8710,7 +8710,7 @@ dependencies = [
 [[package]]
 name = "move-coverage"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "bcs 0.1.4",
@@ -8729,7 +8729,7 @@ dependencies = [
 [[package]]
 name = "move-disassembler"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "clap 4.5.17",
@@ -8746,7 +8746,7 @@ dependencies = [
 [[package]]
 name = "move-docgen"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "clap 4.5.17",
@@ -8765,7 +8765,7 @@ dependencies = [
 [[package]]
 name = "move-errmapgen"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "move-command-line-common",
@@ -8777,7 +8777,7 @@ dependencies = [
 [[package]]
 name = "move-ir-compiler"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "bcs 0.1.4",
@@ -8793,7 +8793,7 @@ dependencies = [
 [[package]]
 name = "move-ir-to-bytecode"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "codespan-reporting",
@@ -8811,7 +8811,7 @@ dependencies = [
 [[package]]
 name = "move-ir-to-bytecode-syntax"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "hex",
@@ -8824,7 +8824,7 @@ dependencies = [
 [[package]]
 name = "move-ir-types"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "hex",
  "move-command-line-common",
@@ -8837,7 +8837,7 @@ dependencies = [
 [[package]]
 name = "move-model"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "codespan",
@@ -8863,7 +8863,7 @@ dependencies = [
 [[package]]
 name = "move-package"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "clap 4.5.17",
@@ -8897,7 +8897,7 @@ dependencies = [
 [[package]]
 name = "move-prover"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "atty",
@@ -8924,7 +8924,7 @@ dependencies = [
 [[package]]
 name = "move-prover-boogie-backend"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "async-trait",
@@ -8953,7 +8953,7 @@ dependencies = [
 [[package]]
 name = "move-prover-bytecode-pipeline"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "abstract-domain-derive",
  "anyhow",
@@ -8970,7 +8970,7 @@ dependencies = [
 [[package]]
 name = "move-resource-viewer"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "hex",
@@ -8997,7 +8997,7 @@ dependencies = [
 [[package]]
 name = "move-stackless-bytecode"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "abstract-domain-derive",
  "codespan-reporting",
@@ -9016,7 +9016,7 @@ dependencies = [
 [[package]]
 name = "move-stdlib"
 version = "0.1.1"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "hex",
@@ -9039,7 +9039,7 @@ dependencies = [
 [[package]]
 name = "move-symbol-pool"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "once_cell",
  "serde",
@@ -9048,7 +9048,7 @@ dependencies = [
 [[package]]
 name = "move-table-extension"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "better_any",
  "bytes 1.7.1",
@@ -9063,7 +9063,7 @@ dependencies = [
 [[package]]
 name = "move-unit-test"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "better_any",
@@ -9091,7 +9091,7 @@ dependencies = [
 [[package]]
 name = "move-vm-runtime"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "better_any",
  "bytes 1.7.1",
@@ -9115,7 +9115,7 @@ dependencies = [
 [[package]]
 name = "move-vm-test-utils"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "anyhow",
  "bytes 1.7.1",
@@ -9130,7 +9130,7 @@ dependencies = [
 [[package]]
 name = "move-vm-types"
 version = "0.1.0"
-source = "git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b#c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b"
+source = "git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899#1d5900920753e93cae0e3e526e16d366851e1899"
 dependencies = [
  "bcs 0.1.4",
  "derivative",
@@ -10638,13 +10638,13 @@ dependencies = [
 [[package]]
 name = "processor"
 version = "1.0.0"
-source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=a11a7ef5346e11a827cec7394a7a3cc4461af820#a11a7ef5346e11a827cec7394a7a3cc4461af820"
+source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58#1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58"
 dependencies = [
  "ahash 0.8.11",
  "allocative",
  "allocative_derive",
  "anyhow",
- "aptos-moving-average 0.1.0 (git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=a11a7ef5346e11a827cec7394a7a3cc4461af820)",
+ "aptos-moving-average 0.1.0 (git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58)",
  "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=338f9a1bcc06f62ce4a4994f1642b9a61b631ee0)",
  "async-trait",
  "bcs 0.1.4",
@@ -12146,7 +12146,7 @@ dependencies = [
 [[package]]
 name = "server-framework"
 version = "1.0.0"
-source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=a11a7ef5346e11a827cec7394a7a3cc4461af820#a11a7ef5346e11a827cec7394a7a3cc4461af820"
+source = "git+https://github.com/movementlabsxyz/aptos-indexer-processors?rev=1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58#1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58"
 dependencies = [
  "anyhow",
  "aptos-system-utils",
@@ -12725,7 +12725,7 @@ name = "suzuka-client"
 version = "0.0.2"
 dependencies = [
  "anyhow",
- "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b)",
+ "aptos-protos 1.3.0 (git+https://github.com/movementlabsxyz/aptos-core?rev=1d5900920753e93cae0e3e526e16d366851e1899)",
  "aptos-sdk",
  "aptos-types",
  "async-trait",
```

### Cargo.toml
```diff
@@ -112,40 +112,40 @@ serde_yaml = "0.9.34"
 ## Aptos dependencies
 ### We use a forked version so that we can override dependency versions. This is required
 ### to be avoid dependency conflicts with other Sovereign Labs crates.
-aptos-api = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-api-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-bitvec = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-block-executor = { git = "https://github.com/movementlabsxyz/aptos-core.git", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-cached-packages = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-config = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-consensus-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-crypto = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b", features = [
+aptos-api = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-api-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-bitvec = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-block-executor = { git = "https://github.com/movementlabsxyz/aptos-core.git", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-cached-packages = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-config = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-consensus-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-crypto = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899", features = [
     "cloneable-private-keys",
 ] }
-aptos-db = { git = "https://github.com/movementlabsxyz/aptos-core.git", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-executor = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-executor-test-helpers = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-executor-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-faucet-core = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-framework = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-language-e2e-tests = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-mempool = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-proptest-helpers = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-sdk = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-state-view = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-storage-interface = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-temppath = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-vm = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-vm-genesis = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-vm-logging = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-vm-validator = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-logger = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-vm-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-indexer = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-indexer-grpc-fullnode = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-indexer-grpc-table-info = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
-aptos-protos = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "c9d4c2d25dfdde02eb2fd3bf73f39ac9d6b3300b" }
+aptos-db = { git = "https://github.com/movementlabsxyz/aptos-core.git", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-executor = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-executor-test-helpers = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-executor-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-faucet-core = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-framework = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-language-e2e-tests = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-mempool = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-proptest-helpers = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-sdk = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-state-view = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-storage-interface = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-temppath = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-vm = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-vm-genesis = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-vm-logging = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-vm-validator = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-logger = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-vm-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-indexer = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-indexer-grpc-fullnode = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-indexer-grpc-table-info = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
+aptos-protos = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "1d5900920753e93cae0e3e526e16d366851e1899" }
 
 # Indexer
 processor = { git = "https://github.com/movementlabsxyz/aptos-indexer-processors", rev = "1d1d7c72a01a0b5a55477f8fdca59e17c9ce2e58", subdir = "rust" }
```

### protocol-units/execution/dof/src/v1.rs
```diff
@@ -58,13 +58,14 @@ impl DynOptFinExecutor for Executor {
 		(Context, impl Future<Output = Result<(), anyhow::Error>> + Send + 'static),
 		anyhow::Error,
 	> {
-		let (opt_context, transaction_pipe, indexer_runtime) =
+		let (opt_context, transaction_pipe) =
 			self.executor.background(transaction_sender, config)?;
 		let fin_service = self.finality_view.service(
 			opt_context.mempool_client_sender(),
 			config,
 			opt_context.node_config().clone(),
 		);
+		let indexer_runtime = opt_context.run_indexer_grpc_service()?;
 		let background = async move {
 			// The indexer runtime should live as long as the Tx pipe.
 			let _indexer_runtime = indexer_runtime;
```

### protocol-units/execution/fin-view/src/fin_view.rs
```diff
@@ -78,8 +78,7 @@ mod tests {
 		let config = Config::default();
 		let (tx_sender, _tx_receiver) = mpsc::channel(16);
 		let executor = Executor::try_from_config(&config)?;
-		let (context, _transaction_pipe, _indexer_runtime) =
-			executor.background(tx_sender, &config)?;
+		let (context, _transaction_pipe) = executor.background(tx_sender, &config)?;
 		let finality_view = FinalityView::new(context.db_reader());
 		let service = finality_view.service(
 			context.mempool_client_sender(),
```

### protocol-units/execution/opt-executor/src/executor/execution.rs
```diff
@@ -261,8 +261,7 @@ mod tests {
 		let private_key = Ed25519PrivateKey::generate_for_testing();
 		let (tx_sender, _tx_receiver) = mpsc::channel(1);
 		let (executor, config, _tempdir) = Executor::try_test_default(private_key)?;
-		let (context, _transaction_pipe, _indexer_runtime) =
-			executor.background(tx_sender, &config)?;
+		let (context, _transaction_pipe) = executor.background(tx_sender, &config)?;
 		let block_id = HashValue::random();
 		let block_metadata = Transaction::BlockMetadata(BlockMetadata::new(
 			block_id,
@@ -296,8 +295,7 @@ mod tests {
 		let private_key = Ed25519PrivateKey::generate_for_testing();
 		let (tx_sender, _tx_receiver) = mpsc::channel(1);
 		let (executor, config, _tempdir) = Executor::try_test_default(private_key)?;
-		let (context, _transaction_pipe, _indexer_runtime) =
-			executor.background(tx_sender, &config)?;
+		let (context, _transaction_pipe) = executor.background(tx_sender, &config)?;
 		executor.rollover_genesis_now().await?;
 
 		// Initialize a root account using a predefined keypair and the test root address.
@@ -399,8 +397,7 @@ mod tests {
 		let private_key = Ed25519PrivateKey::generate_for_testing();
 		let (tx_sender, _tx_receiver) = mpsc::channel(16);
 		let (executor, config, _tempdir) = Executor::try_test_default(private_key)?;
-		let (context, _transaction_pipe, _indexer_runtime) =
-			executor.background(tx_sender, &config)?;
+		let (context, _transaction_pipe) = executor.background(tx_sender, &config)?;
 		let service = Service::new(&context);
 		executor.rollover_genesis_now().await?;
 
```

### protocol-units/execution/opt-executor/src/executor/initialization.rs
```diff
@@ -1,5 +1,5 @@
 use super::Executor;
-use crate::{bootstrap, indexer::IndexerRuntime, Context, TransactionPipe};
+use crate::{bootstrap, Context, TransactionPipe};
 
 use aptos_config::config::NodeConfig;
 #[cfg(test)]
@@ -58,13 +58,15 @@ impl Executor {
 		Ok((executor, maptos_config, tempdir))
 	}
 
-	/// Creates instance of `Context` and the background `TransactionPipe`
+	/// Creates an instance of [`Context`] and the background [`TransactionPipe`]
 	/// task to process transactions.
+	/// The `Context` must be kept around for as long as the `TransactionPipe`
+	/// task needs to be running.
 	pub fn background(
 		&self,
 		transaction_sender: mpsc::Sender<SignedTransaction>,
 		maptos_config: &Config,
-	) -> anyhow::Result<(Context, TransactionPipe, IndexerRuntime)> {
+	) -> anyhow::Result<(Context, TransactionPipe)> {
 		let mut node_config = NodeConfig::default();
 
 		node_config.indexer.enabled = true;
@@ -111,16 +113,14 @@ impl Executor {
 			Arc::clone(&self.transactions_in_flight),
 			maptos_config.load_shedding.max_transactions_in_flight,
 		);
+
 		let cx = Context::new(
 			self.db().clone(),
 			mempool_client_sender,
 			maptos_config.clone(),
 			node_config,
 		);
 
-		// Start indexer grpc entry point.
-		let indexer_runtime = cx.run_indexer_grpc_service()?;
-
-		Ok((cx, transaction_pipe, indexer_runtime))
+		Ok((cx, transaction_pipe))
 	}
 }
```

### protocol-units/execution/opt-executor/src/service.rs
```diff
@@ -116,8 +116,7 @@ mod tests {
 	async fn test_pipe_mempool_while_server_running() -> Result<(), anyhow::Error> {
 		let (tx_sender, mut tx_receiver) = mpsc::channel(16);
 		let (executor, config, _tempdir) = Executor::try_test_default(GENESIS_KEYPAIR.0.clone())?;
-		let (context, mut transaction_pipe, _indexer_runtime) =
-			executor.background(tx_sender, &config)?;
+		let (context, mut transaction_pipe) = executor.background(tx_sender, &config)?;
 		let service = Service::new(&context);
 		let handle = tokio::spawn(async move { service.run().await });
 
```

### protocol-units/execution/opt-executor/src/transaction_pipe.rs
```diff
@@ -202,8 +202,7 @@ mod tests {
 		let (tx_sender, tx_receiver) = mpsc::channel(16);
 		let (executor, config, _tempdir) =
 			Executor::try_test_default(GENESIS_KEYPAIR.0.clone()).unwrap();
-		let (context, transaction_pipe, _indexer_runtime) =
-			executor.background(tx_sender, &config).unwrap();
+		let (context, transaction_pipe) = executor.background(tx_sender, &config).unwrap();
 		(transaction_pipe, context.mempool_client_sender(), tx_receiver)
 	}
 
@@ -312,8 +311,7 @@ mod tests {
 	async fn test_pipe_mempool_from_api() -> Result<(), anyhow::Error> {
 		let (tx_sender, mut tx_receiver) = mpsc::channel(16);
 		let (executor, config, _tempdir) = Executor::try_test_default(GENESIS_KEYPAIR.0.clone())?;
-		let (context, mut transaction_pipe, _indexer_runtime) =
-			executor.background(tx_sender, &config)?;
+		let (context, mut transaction_pipe) = executor.background(tx_sender, &config)?;
 		let service = Service::new(&context);
 
 		#[allow(unreachable_code)]
@@ -342,8 +340,7 @@ mod tests {
 	async fn test_repeated_pipe_mempool_from_api() -> Result<(), anyhow::Error> {
 		let (tx_sender, mut tx_receiver) = mpsc::channel(16);
 		let (executor, config, _tempdir) = Executor::try_test_default(GENESIS_KEYPAIR.0.clone())?;
-		let (context, mut transaction_pipe, _indexer_runtime) =
-			executor.background(tx_sender, &config)?;
+		let (context, mut transaction_pipe) = executor.background(tx_sender, &config)?;
 		let service = Service::new(&context);
 
 		#[allow(unreachable_code)]
```
