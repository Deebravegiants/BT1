# [?] fix(anvil): handle BlockTransactions::Uncle without panic (#14135)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-04-07
Source: https://github.com/foundry-rs/foundry/commit/3d26ca00d8e1097b63bb3a35ebb374e5b1928a1b
Type: security-commit

## Details
fix(anvil): handle BlockTransactions::Uncle without panic (#14135)

## Patch
### crates/anvil/src/eth/backend/fork.rs
```diff
@@ -383,8 +383,7 @@ impl<N: Network> ClientFork<N> {
                         return self.transaction_by_hash(*tx_hash).await;
                     }
                 }
-                // TODO(evalir): Is it possible to reach this case? Should we support it
-                BlockTransactions::Uncle => panic!("Uncles not supported"),
+                BlockTransactions::Uncle => {}
             }
         }
         Ok(None)
@@ -408,8 +407,7 @@ impl<N: Network> ClientFork<N> {
                         return self.transaction_by_hash(*tx_hash).await;
                     }
                 }
-                // TODO(evalir): Is it possible to reach this case? Should we support it
-                BlockTransactions::Uncle => panic!("Uncles not supported"),
+                BlockTransactions::Uncle => {}
             }
         }
         Ok(None)
```
