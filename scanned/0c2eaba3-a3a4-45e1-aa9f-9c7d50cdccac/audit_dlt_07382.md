# [?] Create dependency review workflow for vulnerability checks (#16750)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2025-03-13
Source: https://github.com/smartcontractkit/chainlink/commit/94fe39935a72b0f5d9bd1725df7252b0c6e317c8
Type: security-commit

## Details
Create dependency review workflow for vulnerability checks (#16750)

* Create dependency review workflow for vulnerability checks

* Test adding a vulnerable module

* Use main for now

* Fix require

* Use version with incompatible annotation

* Revert go.mod vuln test

* Use versioned action

## Patch
### .github/workflows/dependency-review.yml
```diff
@@ -0,0 +1,22 @@
+name: Dependency Review
+description: Run dependency review for vulnerabilities.
+
+on:
+  pull_request:
+
+permissions: {}
+
+jobs:
+  dependency-review:
+    permissions:
+      contents: read
+    runs-on: ubuntu-latest
+    steps:
+      - uses: actions/checkout@v4
+        with:
+          fetch-depth: 1
+          persist-credentials: false
+      - name: Vulnerability Check
+        uses: smartcontractkit/.github/actions/dependency-review@0cc355785130a83a540187b609c5521094baed92 # dependency-review@1.0.0
+        with:
+          config-preset: default-vulnerability-check-high
```
