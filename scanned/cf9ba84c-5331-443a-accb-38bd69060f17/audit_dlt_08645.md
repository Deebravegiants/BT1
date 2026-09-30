# [?] fix DataLayer deadlock (#15971)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2023-08-15
Source: https://github.com/Chia-Network/chia-blockchain/commit/f1ad0d29d2de8ae94b02a8c5edf9456e593d125a
Type: security-commit

## Details
fix DataLayer deadlock (#15971)

* fix DataLayer deadlock

* less consistent, less diff

* remove comment

* add test for deadlock

* adjust

## Patch
### chia/data_layer/data_layer.py
```diff
@@ -72,7 +72,6 @@ class DataLayer:
     wallet_id: uint64
     initialized: bool
     none_bytes: bytes32
-    lock: asyncio.Lock
     _server: Optional[ChiaServer]
     downloaders: List[str]
     uploaders: List[str]
@@ -115,7 +114,6 @@ def __init__(
         self.server_files_location = path_from_root(self.root_path, server_files_replaced)
         self.server_files_location.mkdir(parents=True, exist_ok=True)
         self.none_bytes = bytes32([0] * 32)
-        self.lock = asyncio.Lock()
         self._server = None
         self.downloaders = downloaders
         self.uploaders = uploaders
@@ -185,8 +183,7 @@ async def batch_insert(
     ) -> bytes32:
         async with self.data_store.transaction():
             # Make sure we update based on the latest confirmed root.
-            async with self.lock:
-                await self._update_confirmation_status(tree_id=tree_id)
+            await self._update_confirmation_status(tree_id=tree_id)
             pending_root: Optional[Root] = await self.data_store.get_pending_root(tree_id=tree_id)
             if pending_root is not None:
                 raise Exception("Already have a pending root waiting for confirmation.")
@@ -214,8 +211,7 @@ async def publish_update(
         fee: uint64,
     ) -> TransactionRecord:
         # Make sure we update based on the latest confirmed root.
-        async with self.lock:
-            await self._update_confirmation_status(tree_id=tree_id)
+        await self._update_confirmation_status(tree_id=tree_id)
         pending_root: Optional[Root] = await self.data_store.get_pending_root(tree_id=tree_id)
         if pending_root is None:
             raise Exception("Latest root is already confirmed.")
@@ -236,38 +232,33 @@ async def get_key_value_hash(
         root_hash: Optional[bytes32] = None,
     ) -> bytes32:
         async with self.data_store.transaction():
-            async with self.lock:
-                await self._update_confirmation_status(tree_id=store_id)
+            await self._update_confirmation_status(tree_id=store_id)
             node = await self.data_store.get_node_by_key(tree_id=store_id, key=key, root_hash=root_hash)
             return node.hash
 
     async def get_value(self, store_id: bytes32, key: bytes, root_hash: Optional[bytes32] = None) -> Optional[bytes]:
         async with self.data_store.transaction():
-            async with self.lock:
-                await self._update_confirmation_status(tree_id=store_id)
+            await self._update_confirmation_status(tree_id=store_id)
             res = await self.data_store.get_node_by_key(tree_id=store_id, key=key, root_hash=root_hash)
             if res is None:
                 self.log.error("Failed to fetch key")
                 return None
             return res.value
 
     async def get_keys_values(self, store_id: bytes32, root_hash: Optional[bytes32]) -> List[TerminalNode]:
-        async with self.lock:
-            await self._update_confirmation_status(tree_id=store_id)
+        await self._update_confirmation_status(tree_id=store_id)
         res = await self.data_store.get_keys_values(store_id, root_hash)
         if res is None:
             self.log.error("Failed to fetch keys values")
         return res
 
     async def get_keys(self, store_id: bytes32, root_hash: Optional[bytes32]) -> List[bytes]:
-        async with self.lock:
-            await self._update_confirmation_status(tree_id=store_id)
+        await self._update_confirmation_status(tree_id=store_id)
         res = await self.data_store.get_keys(store_id, root_hash)
         return res
 
     async def get_ancestors(self, node_hash: bytes32, store_id: bytes32) -> List[InternalNode]:
-        async with self.lock:
-            await self._update_confirmation_status(tree_id=store_id)
+        await self._update_confirmation_status(tree_id=store_id)
 
         res = await self.data_store.get_ancestors(node_hash=node_hash, tree_id=store_id)
         if res is None:
@@ -281,8 +272,7 @@ async def get_root(self, store_id: bytes32) -> Optional[SingletonRecord]:
         return latest
 
     async def get_local_root(self, store_id: bytes32) -> Optional[bytes32]:
-        async with self.lock:
-            await self._update_confirmation_status(tree_id=store_id)
+        await self._update_confirmation_status(tree_id=store_id)
 
         res = await self.data_store.get_tree_root(tree_id=store_id)
         if res is None:
@@ -368,8 +358,7 @@ async def fetch_and_validate(self, tree_id: bytes32) -> None:
             self.log.info(f"Fetch data: No data on chain for {tree_id}.")
             return
 
-        async with self.lock:
-            await self._update_confirmation_status(tree_id=tree_id)
+        await self._update_confirmation_status(tree_id=tree_id)
 
         if not await self.data_store.tree_id_exists(tree_id=tree_id):
             await self.data_store.create_tree(tree_id=tree_id, status=Status.COMMITTED)
@@ -452,8 +441,7 @@ async def upload_files(self, tree_id: bytes32) -> None:
         if singleton_record is None:
             self.log.info(f"Upload files: no on-chain record for {tree_id}.")
             return
-        async with self.lock:
-            await self._update_confirmation_status(tree_id=tree_id)
+        await self._update_confirmation_status(tree_id=tree_id)
 
         root = await self.data_store.get_tree_root(tree_id=tree_id)
         publish_generation = min(singleton_record.generation, 0 if root is None else root.generation)
@@ -671,8 +659,7 @@ async def process_offered_stores(self, offer_stores: Tuple[OfferStore, ...]) ->
         async with self.data_store.transaction():
             our_store_proofs: Dict[bytes32, StoreProofs] = {}
             for offer_store in offer_stores:
-                async with self.lock:
-                    await self._update_confirmation_status(tree_id=offer_store.store_id)
+                await self._update_confirmation_status(tree_id=offer_store.store_id)
 
                 changelist = await self.build_offer_changelist(
                     store_id=offer_store.store_id,
@@ -869,8 +856,7 @@ async def cancel_offer(self, trade_id: bytes32, secure: bool, fee: uint64) -> No
                 await self.data_store.clear_pending_roots(tree_id=store_id)
 
     async def get_sync_status(self, store_id: bytes32) -> SyncStatus:
-        async with self.lock:
-            await self._update_confirmation_status(tree_id=store_id)
+        await self._update_confirmation_status(tree_id=store_id)
 
         if not await self.data_store.tree_id_exists(tree_id=store_id):
             raise Exception(f"No tree id stored in the local database for {store_id}")
```

### tests/core/data_layer/test_data_rpc.py
```diff
@@ -7,10 +7,12 @@
 import json
 import os
 import sys
+import time
 from dataclasses import dataclass
 from pathlib import Path
 from typing import Any, AsyncIterator, Dict, List, Optional, Tuple
 
+import anyio
 import pytest
 import pytest_asyncio
 
@@ -30,12 +32,12 @@
 from chia.simulator.full_node_simulator import FullNodeSimulator, backoff_times
 from chia.simulator.setup_nodes import SimulatorsAndWalletsServices
 from chia.simulator.simulator_protocol import FarmNewBlockProtocol
-from chia.simulator.time_out_assert import time_out_assert
+from chia.simulator.time_out_assert import adjusted_timeout, time_out_assert
 from chia.types.blockchain_format.sized_bytes import bytes32
 from chia.types.peer_info import PeerInfo
 from chia.util.byte_types import hexstr_to_bytes
 from chia.util.config import save_config
-from chia.util.ints import uint16, uint32
+from chia.util.ints import uint16, uint32, uint64
 from chia.wallet.trading.offer import Offer as TradingOffer
 from chia.wallet.transaction_record import TransactionRecord
 from chia.wallet.wallet import Wallet
@@ -1955,3 +1957,58 @@ async def test_clear_pending_roots(
             assert False, "unhandled parametrization"
 
         assert cleared_root == {"success": True, "root": pending_root.marshal()}
+
+
+@pytest.mark.asyncio
+async def test_issue_15955_deadlock(
+    self_hostname: str, one_wallet_and_one_simulator_services: SimulatorsAndWalletsServices, tmp_path: Path
+) -> None:
+    wallet_rpc_api, full_node_api, wallet_rpc_port, ph, bt = await init_wallet_and_node(
+        self_hostname, one_wallet_and_one_simulator_services
+    )
+
+    wallet_node = wallet_rpc_api.service
+    wallet = wallet_node.wallet_state_manager.main_wallet
+
+    interval = 1
+    config = bt.config
+    config["data_layer"]["manage_data_interval"] = interval
+    bt.change_config(new_config=config)
+
+    async with init_data_layer(wallet_rpc_port=wallet_rpc_port, bt=bt, db_path=tmp_path) as data_layer:
+        # get some xch
+        await full_node_api.farm_blocks_to_wallet(count=1, wallet=wallet)
+        await full_node_api.wait_for_wallet_synced(wallet_node)
+
+        # create a store
+        transaction_records, tree_id = await data_layer.create_store(fee=uint64(0))
+        await full_node_api.process_transaction_records(records=transaction_records)
+        await full_node_api.wait_for_wallet_synced(wallet_node)
+        assert await check_singleton_confirmed(dl=data_layer, tree_id=tree_id)
+
+        # insert a key and value
+        key = b"\x00"
+        value = b"\x01" * 10_000
+        transaction_record = await data_layer.batch_update(
+            tree_id=tree_id,
+            changelist=[{"action": "insert", "key": key, "value": value}],
+            fee=uint64(0),
+        )
+        await full_node_api.process_transaction_records(records=[transaction_record])
+        await full_node_api.wait_for_wallet_synced(wallet_node)
+        assert await check_singleton_confirmed(dl=data_layer, tree_id=tree_id)
+
+        # get the value a bunch through several periodic data management cycles
+        concurrent_requests = 10
+        time_per_request = 2
+        timeout = concurrent_requests * time_per_request
+
+        duration = 10 * interval
+        start = time.monotonic()
+        end = start + duration
+
+        while time.monotonic() < end:
+            with anyio.fail_after(adjusted_timeout(timeout)):
+                await asyncio.gather(
+                    *(asyncio.create_task(data_layer.get_value(store_id=tree_id, key=key)) for _ in range(10))
+                )
```
