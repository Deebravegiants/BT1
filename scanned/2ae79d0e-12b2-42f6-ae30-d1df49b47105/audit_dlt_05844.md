# [?] Fix deadlock when creating the DataLayer wallet during sync (#21225)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2026-08-04
Source: https://github.com/Chia-Network/chia-blockchain/commit/d1d9a2b40b29cca03eae9e37d5e05dfe3f4a8a55
Type: security-commit

## Details
Fix deadlock when creating the DataLayer wallet during sync (#21225)

The wallet sync path holds WalletStateManager.lock for the duration of
sync. When _add_coin_states discovers a DataLayer launcher and no
DataLayer wallet exists yet, it called
get_dl_wallet(create_if_not_found=True), which re-acquires the same
non-reentrant asyncio.Lock, deadlocking the sync task. Create the
wallet directly at the sync call site instead, leaving get_dl_wallet
unchanged for RPC callers.

Regression from #20320 (baf8bd05c0).

## Patch
### chia/_tests/wallet/test_wallet_state_manager.py
```diff
@@ -7,29 +7,35 @@
 from types import SimpleNamespace
 from typing import cast
 
+import anyio
 import pytest
 from chia_rs import CoinState, G2Element
 from chia_rs.sized_bytes import bytes32
 from chia_rs.sized_ints import uint32, uint64
+from pytest_mock import MockerFixture
 
 from chia._tests.conftest import ConsensusMode
 from chia._tests.environments.wallet import WalletStateTransition, WalletTestFramework
 from chia._tests.util.setup_nodes import OldSimulatorsAndWallets
 from chia._tests.util.time_out_assert import time_out_assert
+from chia.data_layer.data_layer_wallet import DataLayerWallet
 from chia.protocols.outbound_message import NodeType
 from chia.types.blockchain_format.coin import Coin
 from chia.types.blockchain_format.program import Program
 from chia.types.coin_spend import make_spend
 from chia.types.peer_info import PeerInfo
+from chia.util.timing import adjusted_timeout
 from chia.wallet import wallet_state_manager as wsm_mod
 from chia.wallet.derivation_record import DerivationRecord
 from chia.wallet.derive_keys import master_sk_to_wallet_sk, master_sk_to_wallet_sk_unhardened
 from chia.wallet.nft_wallet.nft_wallet import NFTWallet
 from chia.wallet.nft_wallet.uncurry_nft import NFTCoinData, UncurriedNFT
 from chia.wallet.remote_wallet.remote_wallet import RemoteWallet
+from chia.wallet.singleton import SINGLETON_LAUNCHER_PUZZLE_HASH
 from chia.wallet.transaction_record import TransactionRecord
 from chia.wallet.util.transaction_type import TransactionType
 from chia.wallet.util.wallet_types import WalletType
+from chia.wallet.wallet_coin_record import WalletCoinRecord
 from chia.wallet.wallet_request_types import (
     CreateNewWallet,
     CreateNewWalletType,
@@ -87,6 +93,69 @@ async def test_set_sync_mode_exception(simulator_and_wallet: OldSimulatorsAndWal
         raise Exception
 
 
+@pytest.mark.limit_consensus_modes(allowed=[ConsensusMode.HARD_FORK_2_0])
+@pytest.mark.anyio
+async def test_create_dl_wallet_during_sync(
+    simulator_and_wallet: OldSimulatorsAndWallets,
+    self_hostname: str,
+    mocker: MockerFixture,
+) -> None:
+    full_nodes, [(wallet_node, wallet_server)], _ = simulator_and_wallet
+    await wallet_server.start_client(
+        PeerInfo(self_hostname, full_nodes[0].full_node.server.get_port()),
+        None,
+    )
+    peer = wallet_node.server.get_connections(NodeType.FULL_NODE)[0]
+    wallet_state_manager = wallet_node.wallet_state_manager
+
+    parent_coin = Coin(bytes32.secret(), bytes32.secret(), uint64(1))
+    await wallet_state_manager.coin_store.add_coin_record(
+        WalletCoinRecord(
+            parent_coin,
+            uint32(1),
+            uint32(0),
+            False,
+            False,
+            WalletType.STANDARD_WALLET,
+            1,
+        )
+    )
+    launcher_coin = Coin(parent_coin.name(), SINGLETON_LAUNCHER_PUZZLE_HASH, uint64(1))
+    launcher_state = CoinState(launcher_coin, uint32(2), uint32(2))
+    second_launcher_coin = Coin(parent_coin.name(), SINGLETON_LAUNCHER_PUZZLE_HASH, uint64(2))
+    second_launcher_state = CoinState(second_launcher_coin, uint32(2), uint32(2))
+    launcher_spend = make_spend(launcher_coin, Program.to(1), Program.to(1))
+    inner_puzzle_hash = bytes32.secret()
+
+    mocker.patch.object(wallet_node, "fetch_children", return_value=[launcher_state, second_launcher_state])
+    mocker.patch.object(wsm_mod, "fetch_coin_spend_for_coin_state", return_value=launcher_spend)
+    mocker.patch.object(wsm_mod, "solution_to_pool_state", side_effect=ValueError)
+    mocker.patch.object(DataLayerWallet, "match_dl_launcher", return_value=(True, inner_puzzle_hash))
+    mocker.patch.object(wallet_state_manager.puzzle_store, "puzzle_hash_exists", return_value=True)
+    track_new_launcher_id = mocker.patch.object(DataLayerWallet, "track_new_launcher_id")
+
+    coin_states = [CoinState(parent_coin, uint32(2), uint32(1))]
+
+    with anyio.fail_after(adjusted_timeout(10)):
+        async with assert_sync_mode(wallet_state_manager, uint32(2)):
+            assert await wallet_state_manager.add_coin_states(coin_states, peer, None)
+
+    assert len(await wallet_state_manager.get_all_wallet_info_entries(wallet_type=WalletType.DATA_LAYER)) == 1
+    track_new_launcher_id.assert_any_await(
+        launcher_coin.name(),
+        peer,
+        spend=launcher_spend,
+        height=uint32(2),
+    )
+    track_new_launcher_id.assert_any_await(
+        second_launcher_coin.name(),
+        peer,
+        spend=launcher_spend,
+        height=uint32(2),
+    )
+    assert track_new_launcher_id.await_count == 2
+
+
 @pytest.mark.parametrize("hardened", [True, False])
 @pytest.mark.limit_consensus_modes(allowed=[ConsensusMode.HARD_FORK_2_0])
 @pytest.mark.anyio
```

### chia/wallet/wallet_state_manager.py
```diff
@@ -2190,7 +2190,12 @@ async def _add_coin_states(
                                     and inner_puzhash is not None
                                     and (await self.puzzle_store.puzzle_hash_exists(inner_puzhash))
                                 ):
-                                    dl_wallet = await self.get_dl_wallet(create_if_not_found=True)
+                                    # Cannot use get_dl_wallet(create_if_not_found=True) here: it
+                                    # acquires self.lock, which the sync path already holds.
+                                    try:
+                                        dl_wallet = await self.get_dl_wallet()
+                                    except ValueError:
+                                        dl_wallet = await DataLayerWallet.create_new_dl_wallet(self)
                                     await dl_wallet.track_new_launcher_id(
                                         child.coin.name(),
                                         peer,
```
