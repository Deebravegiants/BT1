# [?] rpc: fix possible deadlock in rpc (#26051)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2022-06-23
Source: https://github.com/solana-labs/solana/commit/113b161ba9b8a9e11ec50f4dfcc4860fac82e91a
Type: security-commit

## Details
rpc: fix possible deadlock in rpc (#26051)

## Patch
### rpc/src/rpc.rs
```diff
@@ -1431,12 +1431,12 @@ impl JsonRpcRequestProcessor {
         bank: &Arc<Bank>,
     ) -> Option<TransactionStatus> {
         let (slot, status) = bank.get_signature_status_slot(&signature)?;
-        let r_block_commitment_cache = self.block_commitment_cache.read().unwrap();
 
         let optimistically_confirmed_bank = self.bank(Some(CommitmentConfig::confirmed()));
         let optimistically_confirmed =
             optimistically_confirmed_bank.get_signature_status_slot(&signature);
 
+        let r_block_commitment_cache = self.block_commitment_cache.read().unwrap();
         let confirmations = if r_block_commitment_cache.root() >= slot
             && is_finalized(&r_block_commitment_cache, bank, &self.blockstore, slot)
         {
```
