# [?] Merge pull request from GHSA-24jr-26x3-97g2

## Summary
Severity: Unknown
Chain: Bridge
Component: Near-One/rainbow-bridge
Published: 2021-01-27
Source: https://github.com/Near-One/rainbow-bridge/commit/12ff89624142ac858539fb96fa21230f52861389
Type: security-commit

## Details
Merge pull request from GHSA-24jr-26x3-97g2

* fix: Use difficulty from parent header

* Revert part for hash/difficulty check back to the current header

## Patch
### contracts/near/eth-client/src/lib.rs
```diff
@@ -366,8 +366,8 @@ impl EthClient {
         //
         U256((result.0).0.into()) < U256(ethash::cross_boundary(header.difficulty.0))
             && (!self.validate_ethash
-                || (header.difficulty < header.difficulty * 101 / 100
-                    && header.difficulty > header.difficulty * 99 / 100))
+                || (header.difficulty < prev.difficulty * 101 / 100
+                    && header.difficulty > prev.difficulty * 99 / 100))
             && header.gas_used <= header.gas_limit
             && header.gas_limit < prev.gas_limit * 1025 / 1024
             && header.gas_limit > prev.gas_limit * 1023 / 1024
```
