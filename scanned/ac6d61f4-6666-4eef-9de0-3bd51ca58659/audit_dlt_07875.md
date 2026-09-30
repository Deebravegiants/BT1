# [?] bump json-rpc, for potential `nil` http crash (fixes 4118) (#4125)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-09-16
Source: https://github.com/status-im/nimbus-eth2/commit/9df08576a15ade29700fa7d7cc71ad088d87a678
Type: security-commit

## Details
bump json-rpc, for potential `nil` http crash (fixes 4118) (#4125)

* bump json-rpc, for potential `nil` http crash (fixes #4118)

* bump

## Patch
### vendor/nim-json-rpc
```diff
@@ -1 +1 @@
-Subproject commit c8cbe08de756d65e7d085c409dfcb5edfba4aa5d
+Subproject commit 7c80b758566950950ab5e3b29fe7f38c3b8168b0
```
