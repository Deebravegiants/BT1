# [?] [fix] #3195: Also panic when receiving rejected genesis.

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2023-06-23
Source: https://github.com/hyperledger-iroha/iroha/commit/da74b8c29f26670db5639503c5c141363aa05820
Type: security-commit

## Details
[fix] #3195: Also panic when receiving rejected genesis.

Signed-off-by: Sam H. Smith <sam.henning.smith@protonmail.com>

## Patch
### core/src/sumeragi/main_loop.rs
```diff
@@ -221,6 +221,15 @@ impl Sumeragi {
                     };
 
                     if block.is_genesis() {
+                        match &block {
+                            VersionedCommittedBlock::V1(block) => {
+                                assert!(
+                                    !block.transactions.iter().any(|tx| tx.error.is_some()),
+                                    "Genesis transaction set contains invalid transactions"
+                                );
+                            }
+                        }
+
                         self.commit_block(block);
                         return Err(EarlyReturn::GenesisBlockReceivedAndCommitted);
                     }
```
