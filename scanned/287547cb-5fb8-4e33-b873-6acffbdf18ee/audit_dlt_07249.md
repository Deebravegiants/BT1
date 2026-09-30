# [?] .github/workflows: add cosmos/gosec vulnerability scanner for each Push/PR (#9464)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2022-09-23
Source: https://github.com/cometbft/cometbft/commit/ed68aadd2bde64491dbb6f8c2c27ee9ee95bbe79
Type: security-commit

## Details
.github/workflows: add cosmos/gosec vulnerability scanner for each Push/PR (#9464)

Adds a code vulnerability scanner that'll flag issues and issue advisories from cosmos/gosec https://github.com/cosmos/gosec

## Patch
### .github/workflows/gosec.yml
```diff
@@ -0,0 +1,41 @@
+name: Run Gosec
+on:
+  pull_request:
+    paths:
+      - '**/*.go'
+      - 'go.mod'
+      - 'go.sum'
+  push:
+    branches:
+      - main
+      - 'feature/*'
+      - 'v0.37.x'
+      - 'v0.34.x'
+    paths:
+      - '**/*.go'
+      - 'go.mod'
+      - 'go.sum'
+
+jobs:
+  Gosec:
+    permissions:
+      security-events: write
+
+    runs-on: ubuntu-latest
+    env:
+      GO111MODULE: on
+    steps:
+      - name: Checkout Source
+        uses: actions/checkout@v3
+
+      - name: Run Gosec Security Scanner
+        uses: cosmos/gosec@master
+        with:
+          # Let the report trigger a failure with the Github Security scanner features.
+          args: "-no-fail -fmt sarif -out results.sarif ./..."
+
+      - name: Upload SARIF file
+        uses: github/codeql-action/upload-sarif@v2
+        with:
+          # Path to SARIF file relative to the root of the repository
+          sarif_file: results.sarif
```
