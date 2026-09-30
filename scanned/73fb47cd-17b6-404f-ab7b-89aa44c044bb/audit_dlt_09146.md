# [?] [DX-252] Fix Flakeguard Panics (#16874)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2025-03-21
Source: https://github.com/smartcontractkit/chainlink/commit/8dbf0b7761c5e79cc527adce7cc3ff2c5feb0253
Type: security-commit

## Details
[DX-252] Fix Flakeguard Panics (#16874)

* Fix flakeguard panics

* Update to proper version

## Patch
### .github/workflows/flakeguard.yml
```diff
@@ -136,7 +136,7 @@ jobs:
       - name: Install flakeguard
         if: ${{ inputs.runAllTests == false }}
         shell: bash
-        run: go install github.com/smartcontractkit/chainlink-testing-framework/tools/flakeguard@63eefaae8f1aab2716f462c7b286f98866018977 # flakguard@0.1.0
+        run: go install github.com/smartcontractkit/chainlink-testing-framework/tools/flakeguard@ba69ae1d8ddee8b9bbc90f6e042c5d1ce6004697 # flakguard@0.1.0
 
       - name: Find new or updated test packages
         if: ${{ inputs.runAllTests == false && env.RUN_CUSTOM_TEST_PACKAGES == '' }}
@@ -331,7 +331,7 @@ jobs:
 
       - name: Install flakeguard
         shell: bash
-        run: go install github.com/smartcontractkit/chainlink-testing-framework/tools/flakeguard@63eefaae8f1aab2716f462c7b286f98866018977 # flakguard@0.1.0
+        run: go install github.com/smartcontractkit/chainlink-testing-framework/tools/flakeguard@ba69ae1d8ddee8b9bbc90f6e042c5d1ce6004697 # flakguard@0.1.0
 
       - name: Run tests with flakeguard
         shell: bash
@@ -425,7 +425,7 @@ jobs:
 
       - name: Install flakeguard
         shell: bash
-        run: go install github.com/smartcontractkit/chainlink-testing-framework/tools/flakeguard@63eefaae8f1aab2716f462c7b286f98866018977 # flakguard@0.1.0
+        run: go install github.com/smartcontractkit/chainlink-testing-framework/tools/flakeguard@ba69ae1d8ddee8b9bbc90f6e042c5d1ce6004697 # flakguard@0.1.0
 
       - name: Aggregate Flakeguard Results
         id: results
```

### tools/bin/go_core_ccip_deployment_tests
```diff
@@ -8,7 +8,7 @@ EXTRA_FLAGS=""
 
 if [[ -n "$USE_FLAKEGUARD" ]]; then
   # Install flakeguard
-  go install github.com/smartcontractkit/chainlink-testing-framework/tools/flakeguard@63eefaae8f1aab2716f462c7b286f98866018977
+  go install github.com/smartcontractkit/chainlink-testing-framework/tools/flakeguard@9023a8cfa4d119214b965e04653179b6d2052510
   # Install gotestsum to parse JSON test outputs from flakeguard to console outputs
   go install gotest.tools/gotestsum@latest
 
```

### tools/bin/go_core_tests
```diff
@@ -9,7 +9,7 @@ EXTRA_FLAGS="-timeout 20m"
 
 if [[ -n "$USE_FLAKEGUARD" ]]; then
   # Install flakeguard
-  go install github.com/smartcontractkit/chainlink-testing-framework/tools/flakeguard@63eefaae8f1aab2716f462c7b286f98866018977
+  go install github.com/smartcontractkit/chainlink-testing-framework/tools/flakeguard@9023a8cfa4d119214b965e04653179b6d2052510
   # Install gotestsum to parse JSON test outputs from flakeguard to console outputs
   go install gotest.tools/gotestsum@latest
   # Make sure bins are in PATH
```
