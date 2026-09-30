# [?] fix: State Sync Header Request no longer crashes a node (#10313)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2023-12-11
Source: https://github.com/near/nearcore/commit/add31871cbed7f650d83094761abea32a379d2c3
Type: security-commit

## Details
fix: State Sync Header Request no longer crashes a node (#10313)

## Patch
### chain/chain/src/chain.rs
```diff
@@ -3006,7 +3006,11 @@ impl Chain {
             );
 
             let mut root_proofs_cur = vec![];
-            assert_eq!(receipt_proofs.len(), block_header.chunks_included() as usize);
+            if receipt_proofs.len() != block_header.chunks_included() as usize {
+                // Happens if a node doesn't track all shards and can't provide
+                // all incoming receipts to a chunk.
+                return Err(Error::Other("Not tracking all shards".to_owned()));
+            }
             for receipt_proof in receipt_proofs.iter() {
                 let ReceiptProof(receipts, shard_proof) = receipt_proof;
                 let ShardProof { from_shard_id, to_shard_id: _, proof } = shard_proof;
```
