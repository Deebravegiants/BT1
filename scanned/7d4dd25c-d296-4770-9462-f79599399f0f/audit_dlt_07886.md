# [?] Fix a crash occurring with --slashing-db-kind=both

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2021-02-22
Source: https://github.com/status-im/nimbus-eth2/commit/3f6834cce7b60581cfe3cdd9946e28bdc6d74176
Type: security-commit

## Details
Fix a crash occurring with --slashing-db-kind=both

## Patch
### CHANGELOG.md
```diff
@@ -3,7 +3,7 @@
 
 This release includes important JSON-RPC stability improvements
 and compatibility fixes, which make it possible to use Nimbus
-as a RockerPool operator.
+as a RocketPool operator.
 
 -----
 
```

### vendor/nim-stew
```diff
@@ -1 +1 @@
-Subproject commit a0e8ec451ecb4449657f0be7b49fc99641cf5bb6
+Subproject commit 42475fd2f1919acd11be2fdc75fd6e2cefc99e90
```
