# [?] Fix panic in pending_runtime_api with Aura consensus env (#814)

## Summary
Severity: Unknown
Chain: Polkadot
Component: polkadot-evm/frontier
Published: 2022-08-15
Source: https://github.com/polkadot-evm/frontier/commit/fdbe44e4ecd84431d93ddde1918e64208e89090a
Type: security-commit

## Details
Fix panic in pending_runtime_api with Aura consensus env (#814)

* Fix pending_runtime_api

* Use sp_api::HeaderT

* Fix lint

* Fix lint

Co-authored-by: icodezjb <icodezjb@users.noreply.github.com>

## Patch
### client/rpc/src/eth/mod.rs
```diff
@@ -38,7 +38,7 @@ use sc_client_api::backend::{Backend, StateBackend, StorageProvider};
 use sc_network::{ExHashT, NetworkService};
 use sc_transaction_pool::{ChainApi, Pool};
 use sc_transaction_pool_api::{InPoolTransaction, TransactionPool};
-use sp_api::{Core, ProvideRuntimeApi};
+use sp_api::{Core, HeaderT, ProvideRuntimeApi};
 use sp_block_builder::BlockBuilder as BlockBuilderApi;
 use sp_blockchain::HeaderBackend;
 use sp_core::hashing::keccak_256;
@@ -482,7 +482,8 @@ where
 		.collect::<Vec<<B as BlockT>::Extrinsic>>();
 	// Manually initialize the overlay.
 	let header = client.header(best).unwrap().unwrap();
-	api.initialize_block(&best, &header)
+	let parent_hash = BlockId::Hash(*header.parent_hash());
+	api.initialize_block(&parent_hash, &header)
 		.map_err(|e| internal_err(format!("Runtime api access error: {:?}", e)))?;
 	// Apply the ready queue to the best block's state.
 	for xt in xts {
```

### ts-tests/tests/test-balance.ts
```diff
@@ -12,6 +12,7 @@ describeWithFrontier("Frontier RPC (Balance)", (context) => {
 	});
 
 	step("balance to be updated after transfer", async function () {
+		await createAndFinalizeBlock(context.web3);
 		this.timeout(15000);
 
 		const value = "0x200"; // 512, must be higher than ExistentialDeposit
```

### ts-tests/tests/test-contract.ts
```diff
@@ -15,6 +15,7 @@ describeWithFrontier("Frontier RPC (Contract)", (context) => {
 	// to spin up a frontier node, it saves a lot of time.
 
 	it("contract creation should return transaction hash", async function () {
+		await createAndFinalizeBlock(context.web3);
 		this.timeout(15000);
 		const tx = await context.web3.eth.accounts.signTransaction(
 			{
```
