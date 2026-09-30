# [?] fix: use read_recursive to avoid reentrant deadlock in `fee_history`.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-01-14
Source: https://github.com/Conflux-Chain/conflux-rust/commit/0dd4af2f789ab63c631f4c4b610e3f1671e0cd90
Type: security-commit

## Details
fix: use read_recursive to avoid reentrant deadlock in `fee_history`.

## Patch
### crates/cfxcore/core/src/consensus/consensus_graph/onchain_blocks_provider.rs
```diff
@@ -114,7 +114,9 @@ impl ConsensusGraph {
     ) -> Result<H256, ProviderBlockError> {
         self.get_height_from_epoch_number(epoch_number)
             .and_then(|height| {
-                self.inner.read().get_pivot_hash_from_epoch_number(height)
+                self.inner
+                    .read_recursive()
+                    .get_pivot_hash_from_epoch_number(height)
             })
     }
 
```

### tests/test_contracts
```diff
@@ -1 +1 @@
-Subproject commit 337ca543ef22d0924d5b9262735e353ea77afaeb
+Subproject commit 57fe8724c252895f4442a71115efa1bcdf1287d4
```
