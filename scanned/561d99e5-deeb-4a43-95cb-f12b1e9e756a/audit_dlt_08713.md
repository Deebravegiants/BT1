# [?] Avoid overflow when adding additional gas

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-05-01
Source: https://github.com/OffchainLabs/nitro/commit/72cd0b0cf29339bfd32ad11f48bfefad4d9fdd4a
Type: security-commit

## Details
Avoid overflow when adding additional gas

Pulls in https://github.com/OffchainLabs/go-ethereum/pull/448

## Patch
### go-ethereum
```diff
@@ -1 +1 @@
-Subproject commit 3083ee833f8181736e694618d198933fca58fbf3
+Subproject commit 25fc5f0842584e72455e4d60a61f035623b1aba0
```
