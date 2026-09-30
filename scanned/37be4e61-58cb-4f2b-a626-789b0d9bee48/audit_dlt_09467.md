# [?] Merge subtensor main (Fireactions CI runners fix) into security/ghsa-2026-012-staking-coldkey-index-unbounded-growth

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-12
Source: https://github.com/RaoFoundation/subtensor/commit/c7e2f1e7a470a2538e58a194ce910dbd2ac79e84
Type: security-commit

## Details
Merge subtensor main (Fireactions CI runners fix) into security/ghsa-2026-012-staking-coldkey-index-unbounded-growth

## Patch
### .github/workflows/cargo-audit.yml
```diff
@@ -13,7 +13,7 @@ concurrency:
 jobs:
   cargo-audit:
     name: cargo audit
-    runs-on: [self-hosted, type-ccx13]
+    runs-on: [self-hosted, fireactions-light]
     if: ${{ !contains(github.event.pull_request.labels.*.name, 'skip-cargo-audit') }}
     steps:
       - name: Check-out repositoroy under $GITHUB_WORKSPACE
```

### .github/workflows/check-bittensor-e2e-tests.yml
```diff
@@ -190,7 +190,7 @@ jobs:
     strategy:
       matrix:
         platform:
-          - runner: [self-hosted, type-ccx33]
+          - runner: [self-hosted, fireactions-heavy]
             triple: x86_64-unknown-linux-gnu
             arch: amd64
         runtime: ["fast-runtime", "non-fast-runtime"]
```

### .github/workflows/check-devnet.yml
```diff
@@ -15,7 +15,7 @@ env:
 jobs:
   check-spec-version:
     name: Check spec_version bump
-    runs-on: [self-hosted, type-ccx33]
+    runs-on: [self-hosted, fireactions-tryruntime]
     if: ${{ !contains(github.event.pull_request.labels.*.name, 'no-spec-version-bump') }}
     steps:
       - name: Dependencies
```

### .github/workflows/check-docker.yml
```diff
@@ -9,7 +9,7 @@ concurrency:
 
 jobs:
   build:
-    runs-on: [self-hosted, type-ccx33]
+    runs-on: [self-hosted, fireactions-heavy]
 
     steps:
       - name: Checkout code
```

### .github/workflows/check-finney.yml
```diff
@@ -15,7 +15,7 @@ env:
 jobs:
   check-spec-version:
     name: Check spec_version bump
-    runs-on: [self-hosted, type-ccx33]
+    runs-on: [self-hosted, fireactions-tryruntime-finney]
     if: ${{ !contains(github.event.pull_request.labels.*.name, 'no-spec-version-bump') }}
     steps:
       - name: Dependencies
```

### .github/workflows/check-node-compat.yml
```diff
@@ -15,7 +15,7 @@ env:
 jobs:
   build:
     name: build ${{ matrix.version.name }}
-    runs-on: [self-hosted, type-ccx33]
+    runs-on: [self-hosted, fireactions-heavy]
     if: contains(github.event.pull_request.labels.*.name, 'check-node-compat')
     env:
         RUST_BACKTRACE: full
@@ -60,7 +60,7 @@ jobs:
           
   test:
     needs: [build]
-    runs-on: [self-hosted, type-ccx33]
+    runs-on: [self-hosted, fireactions-heavy]
     steps:
       - name: Download old node binary
         uses: actions/download-artifact@v4
@@ -85,4 +85,4 @@ jobs:
         
       - name: Run test
         working-directory: ${{ github.workspace }}/.github/workflows/check-node-compat
-        run: npm run test
\ No newline at end of file
+        run: npm run test
```

### .github/workflows/check-rust.yml
```diff
@@ -23,7 +23,7 @@ jobs:
   # runs cargo fmt
   cargo-fmt:
     name: cargo fmt
-    runs-on: [self-hosted, type-ccx13]
+    runs-on: [self-hosted, fireactions-light]
     env:
       RUST_BACKTRACE: full
     steps:
@@ -67,7 +67,7 @@ jobs:
 
   cargo-clippy-default-features:
     name: cargo clippy
-    runs-on: [self-hosted, type-ccx13]
+    runs-on: [self-hosted, fireactions-light]
     env:
       RUST_BACKTRACE: full
       SKIP_WASM_BUILD: 1
@@ -97,7 +97,7 @@ jobs:
 
   cargo-check-lints:
     name: check custom lints
-    runs-on: [self-hosted, type-ccx13]
+    runs-on: [self-hosted, fireactions-light]
     env:
       RUSTFLAGS: -D warnings
       RUST_BACKTRACE: full
@@ -130,7 +130,7 @@ jobs:
 
   cargo-clippy-all-features:
     name: cargo clippy --all-features
-    runs-on: [self-hosted, type-ccx13]
+    runs-on: [self-hosted, fireactions-light]
     env:
       RUST_BACKTRACE: full
       SKIP_WASM_BUILD: 1
@@ -161,7 +161,7 @@ jobs:
   # runs cargo test --workspace --all-features
   cargo-test:
     name: cargo test
-    runs-on: [self-hosted, type-ccx43]
+    runs-on: [self-hosted, fireactions-heavy]
     env:
       RUST_BACKTRACE: full
       SKIP_WASM_BUILD: 1
@@ -191,7 +191,7 @@ jobs:
   # ensures cargo fix has no trivial changes that can be applied
   cargo-fix:
     name: cargo fix
-    runs-on: [self-hosted, type-ccx13]
+    runs-on: [self-hosted, fireactions-light]
     env:
       RUST_BACKTRACE: full
       SKIP_WASM_BUILD: 1
@@ -230,7 +230,7 @@ jobs:
 
   check-feature-propagation:
     name: zepter run check
-    runs-on: [self-hosted, type-ccx13]
+    runs-on: [self-hosted, fireactions-light]
 
     steps:
       - name: Checkout
```

### .github/workflows/check-testnet.yml
```diff
@@ -15,7 +15,7 @@ env:
 jobs:
   check-spec-version:
     name: Check spec_version bump
-    runs-on: [self-hosted, type-ccx33]
+    runs-on: [self-hosted, fireactions-tryruntime]
     if: ${{ !contains(github.event.pull_request.labels.*.name, 'no-spec-version-bump') }}
     steps:
       - name: Dependencies
```

### .github/workflows/contract-tests.yml
```diff
@@ -24,7 +24,7 @@ permissions:
 
 jobs:
   run:
-    runs-on: [self-hosted, type-ccx13]
+    runs-on: [self-hosted, fireactions-light]
     env:
       RUST_BACKTRACE: full
     steps:
```

### .github/workflows/docker-localnet.yml
```diff
@@ -95,7 +95,7 @@ jobs:
       matrix:
         platform:
           # triple names used `in scripts/install_prebuilt_binaries.sh` file
-          - runner: [self-hosted, type-ccx33]
+          - runner: [self-hosted, fireactions-heavy]
             triple: x86_64-unknown-linux-gnu
             arch: amd64
           - runner: [ubuntu-24.04-arm]
@@ -162,7 +162,7 @@ jobs:
   # Collect all artifacts and publish them to docker repo
   docker:
     needs: [setup, artifacts]
-    runs-on: [self-hosted, type-ccx33]
+    runs-on: [self-hosted, fireactions-heavy]
     defaults:
       run:
         working-directory: ${{ github.workspace }}
```

### .github/workflows/docker.yml
```diff
@@ -27,7 +27,7 @@ permissions:
 
 jobs:
   publish:
-    runs-on: [self-hosted, type-ccx53, type-ccx43, type-ccx33]
+    runs-on: [self-hosted, fireactions-heavy]
 
     steps:
       - name: Determine Docker tag and ref
@@ -71,4 +71,4 @@ jobs:
           platforms: linux/amd64,linux/arm64
           tags: |
             ghcr.io/${{ github.repository }}:${{ env.tag }}
-            ${{ env.latest_tag == 'true' && format('ghcr.io/{0}:latest', github.repository) || '' }}
\ No newline at end of file
+            ${{ env.latest_tag == 'true' && format('ghcr.io/{0}:latest', github.repository) || '' }}
```

### .github/workflows/eco-tests.yml
```diff
@@ -17,7 +17,7 @@ env:
 jobs:
   eco-tests:
     name: cargo test (eco-tests)
-    runs-on: [self-hosted, type-ccx43]
+    runs-on: [self-hosted, fireactions-heavy]
     env:
       RUST_BACKTRACE: full
       SKIP_WASM_BUILD: 1
```
