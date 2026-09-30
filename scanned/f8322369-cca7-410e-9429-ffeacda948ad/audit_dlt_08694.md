# [?] Avoid underflow in state transition

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-20
Source: https://github.com/OffchainLabs/nitro/commit/0229be130e55c8f80a484d44439dc9e5da3ea4fe
Type: security-commit

## Details
Avoid underflow in state transition

## Patch
### go-ethereum
```diff
@@ -1 +1 @@
-Subproject commit 0dc16266ed51575c8147b3626ee517cd0d9d7059
+Subproject commit ae7ed10bd1a1156264930e29f92a906fe00f044b
```
