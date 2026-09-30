# [?] Scheduled vulnerability scan of dependencies

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2022-12-15
Source: https://github.com/hyperledger/fabric/commit/54c7e6a5647fcb3832e7dd24fcf53d0fbc43d9b1
Type: security-commit

## Details
Scheduled vulnerability scan of dependencies

Signed-off-by: Mark S. Lewis <mark_lewis@uk.ibm.com>

## Patch
### .github/workflows/vulnerability-scan.yml
```diff
@@ -0,0 +1,34 @@
+# Copyright the Hyperledger Fabric contributors. All rights reserved.
+#
+# SPDX-License-Identifier: Apache-2.0
+
+name: "Security vulnerability scan"
+
+on:
+  schedule:
+    - cron: "50 1 * * *"
+
+permissions:
+  contents: read
+
+jobs:
+  scan:
+    runs-on: ubuntu-22.04
+    strategy:
+      fail-fast: false
+      matrix:
+        ref:
+          - main
+          - release-2.5
+          - release-2.4
+          - release-2.2
+    steps:
+      - uses: actions/checkout@v3
+        with:
+          ref: ${{ matrix.ref }}
+      - name: Set up Go
+        uses: actions/setup-go@v3
+        with:
+          go-version: 1.19
+      - name: Scan
+        run: make scan
```
