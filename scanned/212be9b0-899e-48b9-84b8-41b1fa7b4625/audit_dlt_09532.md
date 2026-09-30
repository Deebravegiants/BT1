# [?] Merge pull request #3581 from peilun-conflux/fix-gas-sum-overflow

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-31
Source: https://github.com/Conflux-Chain/conflux-rust/commit/3472192dfa0ad8b0b4c5a09cbfdd6b05a07aeb3b
Type: security-commit

## Details
Merge pull request #3581 from peilun-conflux/fix-gas-sum-overflow

fix: reject blocks whose packed gas-limit sum overflows U256 (#3581)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

## Patch
### crates/cfxcore/core/src/verification.rs
```diff
@@ -498,7 +498,16 @@ impl VerificationConfig {
     ) -> Result<(), Error> {
         let mut total_gas: SpaceMap<U256> = SpaceMap::default();
         for t in &block.transactions {
-            total_gas[t.space()] += *t.gas_limit();
+            // gas_limit is unbounded on this path, so the per-space sum can
+            // exceed U256; a bare `+=` would panic instead of rejecting.
+            let acc = &mut total_gas[t.space()];
+            *acc = acc.checked_add(*t.gas_limit()).ok_or_else(|| {
+                BlockError::InvalidPackedGasLimit(OutOfBounds {
+                    min: None,
+                    max: Some(*block.block_header.gas_limit()),
+                    found: U256::MAX,
+                })
+            })?;
         }
 
         if block.block_header.height()
@@ -525,7 +534,17 @@ impl VerificationConfig {
             };
 
         let evm_total_gas = total_gas[Space::Ethereum];
-        let block_total_gas = total_gas.map_sum(|x| *x);
+        // native + evm can exceed U256 even when each fits; avoid a
+        // panicking sum.
+        let block_total_gas = total_gas[Space::Native]
+            .checked_add(total_gas[Space::Ethereum])
+            .ok_or_else(|| {
+                BlockError::InvalidPackedGasLimit(OutOfBounds {
+                    min: None,
+                    max: Some(*block.block_header.gas_limit()),
+                    found: U256::MAX,
+                })
+            })?;
 
         if evm_total_gas > evm_space_gas_limit {
             return Err(From::from(BlockError::InvalidPackedGasLimit(
@@ -1113,4 +1132,77 @@ mod tests {
             serde_json::from_str(&serialized).unwrap();
         assert_eq!(epoch_proof, deserialized);
     }
+
+    // A miner can pack transactions whose gas_limit values sum past U256; the
+    // summation used to panic instead of rejecting the block.
+    #[test]
+    fn packed_gas_sum_overflow_is_rejected() {
+        use crate::{
+            core_error::{BlockError, CoreError as Error},
+            verification::{compute_transaction_root, VerificationConfig},
+        };
+        use cfx_executor::{
+            machine::{Machine, VmFactory},
+            spec::CommonParams,
+        };
+        use cfx_types::U256;
+        use cfxkey::{Generator, Random};
+        use primitives::{
+            transaction::native_transaction::{
+                NativeTransaction, TypedNativeTransaction,
+            },
+            Action, Block, BlockHeaderBuilder, Transaction,
+        };
+        use std::sync::Arc;
+
+        let params = CommonParams::default();
+        let chain_id = params.chain_id.read().get_chain_id(1);
+        let machine =
+            Arc::new(Machine::new_with_builtin(params, VmFactory::new(1024)));
+        let config = VerificationConfig::new(
+            false,
+            200,
+            200 * 1024,
+            100_000,
+            128,
+            u64::MAX,
+            machine,
+        );
+
+        let keypair = Random.generate().unwrap();
+        let tx = |nonce: u64| {
+            Arc::new(
+                Transaction::Native(TypedNativeTransaction::Cip155(
+                    NativeTransaction {
+                        nonce: nonce.into(),
+                        gas_price: U256::one(),
+                        // 2^255; two of these sum to 2^256.
+                        gas: U256::one() << 255,
+                        action: Action::Create,
+                        value: U256::zero(),
+                        storage_limit: 0,
+                        epoch_height: 1,
+                        chain_id: chain_id.in_native_space(),
+                        data: vec![],
+                    },
+                ))
+                .sign(keypair.secret()),
+            )
+        };
+        let txs = vec![tx(0), tx(1)];
+
+        let parent = BlockHeaderBuilder::new().with_height(0).build();
+        let header = BlockHeaderBuilder::new()
+            .with_height(1)
+            .with_parent_hash(parent.hash())
+            .with_transactions_root(compute_transaction_root(&txs))
+            .with_gas_limit(30_000_000.into())
+            .build();
+        let block = Block::new(header, txs);
+
+        assert!(matches!(
+            config.verify_sync_graph_ready_block(&block, &parent),
+            Err(Error::Block(BlockError::InvalidPackedGasLimit(_))),
+        ));
+    }
 }
```
