# [?] Fix flaky test_maximum_full_file_count by eliminating race condition (#20704)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2026-03-25
Source: https://github.com/Chia-Network/chia-blockchain/commit/309c279313bc61d8ee98c39da0d000aee23b432e
Type: security-commit

## Details
Fix flaky test_maximum_full_file_count by eliminating race condition (#20704)

* Fix flaky test_maximum_full_file_count by eliminating race condition

The test fails intermittently on macOS CI because farm_block_with_spend
polls the mempool with a blind timeout. When the wallet builds a spend
against stale singleton state, the full node rejects it
(INVALID_SPEND_BUNDLE, status 3), the mempool never reaches count 1,
and the test burns 30 seconds before failing with a misleading timeout.

Three fixes:

1. Add check_mempool_spend_count_or_fail() that inspects the
   transaction's sent_to field on each poll. If any entry has
   MempoolInclusionStatus.FAILED, raise immediately with the rejection
   reason instead of waiting for the timeout.

2. Add a singleton readiness check (check_singleton_confirmed) after
   farm_block_with_spend in the test loop, ensuring the DataLayer
   wallet has processed the previous block's singleton update before
   the next batch_update builds a new spend.

3. Change check_mempool_spend_count to use >= instead of == so
   auto-resends or ancillary transactions don't break the check.

Made-with: Cursor

* Add pragma: no cover to defensive error-handling paths

The check_mempool_spend_count_or_fail helper's RuntimeError raise and
ValueError catch are defensive paths that only fire on mempool rejection
or unexpected errors — neither occurs during happy-path test runs.
Marking them with pragma: no cover matches the existing convention used
throughout this file and resolves the Coveralls coverage gap.

## Patch
### chia/_tests/core/data_layer/test_data_rpc.py
```diff
@@ -63,6 +63,7 @@
 from chia.simulator.block_tools import BlockTools
 from chia.simulator.full_node_simulator import FullNodeSimulator
 from chia.simulator.simulator_protocol import FarmNewBlockProtocol
+from chia.types.mempool_inclusion_status import MempoolInclusionStatus
 from chia.types.peer_info import PeerInfo
 from chia.util.byte_types import hexstr_to_bytes
 from chia.util.config import save_config
@@ -196,17 +197,32 @@ async def is_transaction_confirmed(api: WalletRpcApi, tx_id: bytes32) -> bool:
     return True if TransactionRecord.from_json_dict(val["transaction"]).confirmed else False  # mypy
 
 
+async def check_mempool_spend_count_or_fail(
+    full_node_api: FullNodeSimulator, num_of_spends: int, wallet_rpc_api: WalletRpcApi, tx_id: bytes32
+) -> bool:
+    """Poll mempool count but raise immediately if the transaction was rejected."""
+    try:
+        val = await wallet_rpc_api.get_transaction({"transaction_id": tx_id.hex()})
+        tx_record = TransactionRecord.from_json_dict(val["transaction"])
+        for _, status, error in tx_record.sent_to:
+            if status == MempoolInclusionStatus.FAILED.value:
+                raise RuntimeError(f"Transaction {tx_id} rejected by mempool: {error}")  # pragma: no cover
+    except ValueError:  # pragma: no cover
+        pass  # pragma: no cover
+    return full_node_api.full_node.mempool_manager.mempool.size() >= num_of_spends
+
+
 async def farm_block_with_spend(
     full_node_api: FullNodeSimulator, ph: bytes32, tx_rec: bytes32, wallet_rpc_api: WalletRpcApi
 ) -> None:
-    await time_out_assert(10, check_mempool_spend_count, True, full_node_api, 1)
+    await time_out_assert(10, check_mempool_spend_count_or_fail, True, full_node_api, 1, wallet_rpc_api, tx_rec)
     await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
     await time_out_assert(10, is_transaction_confirmed, True, wallet_rpc_api, tx_rec)
     await full_node_api.wait_for_wallet_synced(wallet_node=wallet_rpc_api.service, timeout=20)
 
 
 def check_mempool_spend_count(full_node_api: FullNodeSimulator, num_of_spends: int) -> bool:
-    return full_node_api.full_node.mempool_manager.mempool.size() == num_of_spends
+    return full_node_api.full_node.mempool_manager.mempool.size() >= num_of_spends
 
 
 async def check_coin_state(wallet_node: WalletNode, coin_id: bytes32) -> bool:
@@ -2287,6 +2303,7 @@ async def test_maximum_full_file_count(
             res = await data_rpc_api.batch_update({"id": store_id.hex(), "changelist": changelist})
             update_tx_rec = res["tx_id"]
             await farm_block_with_spend(full_node_api, ph, update_tx_rec, wallet_rpc_api)
+            await time_out_assert(10, check_singleton_confirmed, True, data_layer, store_id)
             await asyncio.sleep(manage_data_interval * 2)
             root_hash = await data_rpc_api.get_root({"id": store_id.hex()})
             root_hashes.append(root_hash["hash"])
```
