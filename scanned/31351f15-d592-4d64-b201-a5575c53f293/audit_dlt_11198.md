# [?] apollo_mempool_p2p: fix Duration::MAX in tests (prevent overflow on addition) (#14062)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-05-18
Source: https://github.com/starkware-libs/sequencer/commit/47a8fd47ad42ae1b1e17ea0575a33494b4c3906e
Type: security-commit

## Details
apollo_mempool_p2p: fix Duration::MAX in tests (prevent overflow on addition) (#14062)

Signed-off-by: Dori Medini <dori@starkware.co>

## Patch
### crates/apollo_mempool_p2p/src/runner/test.rs
```diff
@@ -32,7 +32,7 @@ use starknet_api::transaction::TransactionHash;
 
 use super::MempoolP2pRunner;
 
-const MAX_TRANSACTION_BATCH_RATE: Duration = Duration::MAX;
+const MAX_TRANSACTION_BATCH_RATE: Duration = Duration::from_secs(3600);
 const MAX_CONCURRENT_GATEWAY_REQUESTS: usize = 10000;
 
 fn setup(
```
