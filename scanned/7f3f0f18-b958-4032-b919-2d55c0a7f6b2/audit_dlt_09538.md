# [?] fix U256 addition overflow issue in tx pool insert operation

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-06-03
Source: https://github.com/Conflux-Chain/conflux-rust/commit/d23a86f412ec49c15a3d98a31d21c06ea686788b
Type: security-commit

## Details
fix U256 addition overflow issue in tx pool insert operation

## Patch
### crates/cfxcore/core/src/transaction_pool/transaction_pool_inner.rs
```diff
@@ -1029,18 +1029,24 @@ impl TransactionPoolInner {
             );
             match transaction.unsigned {
                 Transaction::Native(ref utx) => {
-                    need_balance += utx.value().clone();
+                    need_balance =
+                        need_balance.saturating_add(utx.value().clone());
                     if sponsored_gas == U256::from(0) {
-                        need_balance += estimate_gas_fee;
+                        need_balance =
+                            need_balance.saturating_add(estimate_gas_fee);
                     }
                     if sponsored_storage == 0 {
-                        need_balance += U256::from(*utx.storage_limit())
-                            * *DRIPS_PER_STORAGE_COLLATERAL_UNIT;
+                        need_balance = need_balance.saturating_add(
+                            U256::from(*utx.storage_limit())
+                                * *DRIPS_PER_STORAGE_COLLATERAL_UNIT,
+                        );
                     }
                 }
                 Transaction::Ethereum(ref utx) => {
-                    need_balance += utx.value().clone();
-                    need_balance += estimate_gas_fee;
+                    need_balance =
+                        need_balance.saturating_add(utx.value().clone());
+                    need_balance =
+                        need_balance.saturating_add(estimate_gas_fee);
                 }
             }
 
```
