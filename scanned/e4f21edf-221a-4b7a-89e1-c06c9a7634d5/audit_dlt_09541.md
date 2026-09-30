# [?] fix array index panic when it is empty

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-28
Source: https://github.com/Conflux-Chain/conflux-rust/commit/eb8aa27322f8d20efb4bcf3ff0041ec160bbf898
Type: security-commit

## Details
fix array index panic when it is empty

## Patch
### crates/rpc/rpc-cfx-impl/src/helpers/block_provider.rs
```diff
@@ -58,10 +58,15 @@ pub fn build_block(
                         }
                         Some(total_gas_used)
                     }
-                    None => Some(
-                        execution_result.block_receipts.receipts[tx_len - 1]
-                            .accumulated_gas_used,
-                    ),
+                    None => {
+                        let total_gas_used = if tx_len == 0 {
+                            U256::zero()
+                        } else {
+                            execution_result.block_receipts.receipts[tx_len - 1]
+                                .accumulated_gas_used
+                        };
+                        Some(total_gas_used)
+                    }
                 }
             }
             None => None,
```
