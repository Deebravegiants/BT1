# [?] [fix] #3075: Panic on invalid tx in genesis.

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2023-05-29
Source: https://github.com/hyperledger-iroha/iroha/commit/bf63c6e0133c7a2ed1408ac675abdb1f997ed72f
Type: security-commit

## Details
[fix] #3075: Panic on invalid tx in genesis.

Signed-off-by: Sam H. Smith <sam.henning.smith@protonmail.com>

## Patch
### core/src/sumeragi/main_loop.rs
```diff
@@ -254,6 +254,10 @@ impl Sumeragi {
             wsv: self.wsv.clone(),
         }
         .build();
+        assert!(
+            block.rejected_transactions.is_empty(),
+            "Genesis transaction set contains invalid transactions"
+        );
 
         {
             info!(block_partial_hash = %block.partial_hash(), "Publishing genesis block.");
```
