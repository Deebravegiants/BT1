# [?] Fix race condition with reorged txs (#13366)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2022-09-08
Source: https://github.com/Chia-Network/chia-blockchain/commit/8fe1327f7f9fb6a15507639603469f6c84f3d993
Type: security-commit

## Details
Fix race condition with reorged txs (#13366)

## Patch
### tests/pools/test_pool_rpc.py
```diff
@@ -369,7 +369,15 @@ async def pw_created(check_wallet_id: int) -> bool:
         def mempool_not_empty() -> bool:
             return len(full_node_api.full_node.mempool_manager.mempool.spends.keys()) > 0
 
+        def mempool_empty() -> bool:
+            return len(full_node_api.full_node.mempool_manager.mempool.spends.keys()) == 0
+
+        await client.delete_unconfirmed_transactions("1")
+        await farm_blocks(full_node_api, our_ph_2, 1)
+        await time_out_assert(20, wallet_is_synced, True, wallet_node_0, full_node_api)
+
         for i in range(5):
+            await time_out_assert(10, mempool_empty)
             res = await client.create_new_cat_and_wallet(20)
             summaries_response = await client.get_wallets()
             assert res["success"]
```
