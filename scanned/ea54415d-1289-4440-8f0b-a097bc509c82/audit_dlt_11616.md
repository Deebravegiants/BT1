# [?] Problem: minor security issue in build-rocksdb workflow (#1069)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/chain-main
Published: 2024-07-24
Source: https://github.com/crypto-org-chain/chain-main/commit/5304924fbcb032540de11b9fb3e38b1ace6d1d2b
Type: security-commit

## Details
Problem: minor security issue in build-rocksdb workflow (#1069)

## Patch
### .github/workflows/build.yml
```diff
@@ -137,6 +137,10 @@ jobs:
       matrix:
         os: [ubuntu-latest, macos-latest]
     runs-on: ${{ matrix.os }}
+    permissions:
+      actions: read
+      contents: read
+      security-events: write
     steps:
       - uses: actions/checkout@v3
       - uses: cachix/install-nix-action@v23
```
