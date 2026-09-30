# [?] fix crash when using >1024 file descriptors

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-04-11
Source: https://github.com/status-im/nimbus-eth2/commit/2d3d819fd2601e87825150b7dd8ea4c179d0da00
Type: security-commit

## Details
fix crash when using >1024 file descriptors

* fixes the crash part of #3521, which in turn is a result of the leaks
fixed in #3582

## Patch
### vendor/nim-chronos
```diff
@@ -1 +1 @@
-Subproject commit ae2a87778feb5eba556b5f0c619db67ba3fd6710
+Subproject commit bb4c3298f56ba7bc69fbccd08fd6e5474c410262
```
