The code path is concrete and traceable. Let me verify the early-exit guard that determines whether recovery is possible.

The attack path is fully confirmed. Here is the complete analysis:

---

### Title
Malicious Untrusted Peer Suppresses Singleton Launcher Detection via Empty `RespondChildren`, Permanently Preventing PoolWallet/DataLayerWallet Creation — (`chia/wallet/wallet_state_manager.py`)

### Summary

A malicious untrusted peer can return a valid but empty `RespondChildren` response to a `fetch_children` call inside `_add_coin_states`. This causes the singleton launcher detection loop to be skipped entirely. Because the parent coin is then written to the local DB with the correct spent/created heights, the early-exit guard in subsequent syncs permanently prevents re-processing, leaving the wallet unable to manage any pool or Data Layer singleton created in that transaction.

### Finding Description

**Entrypoint — `fetch_children` accepts empty response from untrusted peer**

`WalletNode.fetch_children` sends `RequestChildren` to the peer and validates the response: [1](#0-0) 

The only hard check is `isinstance(response, RespondChildren)`. For untrusted peers, each returned `CoinState` is individually validated via `validate_received_state_from_peer`, but an empty `coin_states=[]` list passes trivially — the loop body never executes and `validated = []` is returned with no exception raised.

**`_add_coin_states` — launcher detection loop is skipped when `children == []`**

When a spent coin is processed, `fetch_children` is called at line 1911: [2](#0-1) 

With `children = []`, the `WalletCoinRecord` is still created and persisted with the correct `confirmed_block_height` and `spent_block_height`: [3](#0-2) 

The singleton launcher detection loop at line 2161 then iterates over `children`, which is empty, so it is entirely skipped — no `PoolWallet.create` or `dl_wallet.track_new_launcher_id` is ever called: [4](#0-3) 

**Early-exit guard makes the miss permanent**

On every subsequent sync (including reconnection to a trusted peer), `_add_coin_states` checks the local record at the top of the loop: [5](#0-4) 

Because the coin was already written with `confirmed_block_height == coin_state.created_height` and `spent_block_height == coin_state.spent_height`, both conditions are satisfied and `continue` is executed — the coin state is permanently skipped on all future syncs. The singleton launcher detection loop never gets another chance to run for this coin.

**No retry mechanism covers this case**

The `retry_store` is only populated when a `PeerRequestException` or `aiosqlite.Error` is raised: [6](#0-5) 

An empty-list response is not an exception, so the state is never queued for retry.

### Impact Explanation

The wallet permanently loses the ability to manage any pool wallet or Data Layer store whose singleton launcher was created in the suppressed transaction. The `PoolWallet` object is never instantiated, so pool join/leave/claim operations are unavailable. The `DataLayerWallet` never tracks the launcher, so all Data Layer operations for that store are inaccessible. The on-chain singleton continues to exist and accrue rewards/state, but the wallet has no record of it and cannot interact with it without a full DB reset.

### Likelihood Explanation

Any node that can establish an untrusted peer connection to the wallet (the default for light wallets without a configured trusted peer) can execute this attack. The attacker only needs to be connected at the moment the standard wallet coin is spent creating the launcher — a narrow but deterministic window. The attack requires no keys, no cryptographic break, and no privileged access.

### Recommendation

1. **Do not treat an empty `RespondChildren` as authoritative for untrusted peers.** If the wallet has a pending unconfirmed transaction that creates a singleton launcher, and `fetch_children` returns empty from an untrusted peer, the result should be treated as a `PeerRequestException` (triggering the retry store) rather than silently accepted.
2. **Alternatively, do not write the coin record as fully processed until children have been verified.** If `children` is empty and the coin is known to have created outputs (e.g., from the unconfirmed tx record), defer committing the spent record and add it to the retry store.
3. **At minimum, do not allow the early-exit guard to fire when the singleton launcher detection was never attempted** (i.e., when `children` was empty from an untrusted peer for a coin that had unconfirmed outgoing transactions).

### Proof of Concept

```python
# Integration test sketch
# 1. Wallet creates a pool wallet transaction (standard coin → singleton launcher + singleton)
# 2. Transaction is confirmed on-chain
# 3. Before the wallet processes the spend update, intercept fetch_children
#    for the standard coin and return RespondChildren(coin_states=[])
# 4. Allow _add_coin_states to complete
# 5. Assert: wallet has no PoolWallet in wallet_state_manager.wallets
# 6. Reconnect wallet to a trusted full node peer
# 7. Assert: wallet STILL has no PoolWallet (early-exit guard fires, no re-processing)
# 8. Assert: pool_wallet.get_current_state() raises / pool RPC returns error
```

The `test_retry_store` test in `chia/_tests/wallet/sync/test_wallet_sync.py` already demonstrates the `flaky_fetch_children` pattern (raising `PeerRequestException`), but does not cover the silent-empty-list case, which bypasses the retry mechanism entirely. [7](#0-6)

### Citations

**File:** chia/wallet/wallet_node.py (L1822-1833)
```python
        response: RespondChildren | None = await peer.call_api(FullNodeAPI.request_children, RequestChildren(coin_name))
        if response is None or not isinstance(response, RespondChildren):
            raise PeerRequestException(f"Was not able to obtain children {response}")

        if not self.is_trusted(peer):
            request_cache = self.get_cache_for_peer(peer)
            validated = []
            for state in response.coin_states:
                valid = await self.validate_received_state_from_peer(state, peer, request_cache, fork_height)
                if valid:
                    validated.append(state)
            return validated
```

**File:** chia/wallet/wallet_state_manager.py (L1802-1815)
```python
                    if local_record is not None:
                        local_spent = None
                        if local_record.spent_block_height != 0:
                            local_spent = local_record.spent_block_height
                        if (
                            local_spent == coin_state.spent_height
                            and local_record.confirmed_block_height == coin_state.created_height
                            and not (
                                local_record.wallet_type == WalletType.REMOTE
                                and wallet_identifier is not None
                                and wallet_identifier.type != WalletType.REMOTE
                            )
                        ):
                            continue
```

**File:** chia/wallet/wallet_state_manager.py (L1909-1912)
```python
                    elif coin_state.created_height is not None and coin_state.spent_height is not None:
                        self.log.debug("Coin spent: %s", coin_state)
                        children = await self.wallet_node.fetch_children(coin_name, peer=peer, fork_height=fork_height)
                        record = local_record
```

**File:** chia/wallet/wallet_state_manager.py (L1925-1934)
```python
                            record = WalletCoinRecord(
                                coin_state.coin,
                                uint32(coin_state.created_height),
                                uint32(coin_state.spent_height),
                                True,
                                farmer_reward or pool_reward,
                                wallet_identifier.type,
                                wallet_identifier.id,
                            )
                            await self.coin_store.add_coin_record(record)
```

**File:** chia/wallet/wallet_state_manager.py (L2160-2165)
```python
                        # Check if a child is a singleton launcher
                        for child in children:
                            if child.coin.puzzle_hash != SINGLETON_LAUNCHER_HASH:
                                continue
                            if await self.have_a_pool_wallet_with_launched_id(child.coin.name()):
                                continue
```

**File:** chia/wallet/wallet_state_manager.py (L2231-2232)
```python
                if isinstance(e, (PeerRequestException, aiosqlite.Error)):
                    await self.retry_store.add_state(coin_state, peer.peer_node_id, fork_height)
```

**File:** chia/_tests/wallet/sync/test_wallet_sync.py (L1586-1599)
```python
    def flaky_fetch_children(
        flakiness_info: FlakinessInfo,
        func: Callable[[bytes32, WSChiaConnection, uint32 | None], Awaitable[list[CoinState]]],
    ) -> Callable[[bytes32, WSChiaConnection, uint32 | None], Awaitable[list[CoinState]]]:
        async def new_func(
            coin_name: bytes32, peer: WSChiaConnection, fork_height: uint32 | None = None
        ) -> list[CoinState]:
            if flakiness_info.fetch_children_flaky:
                flakiness_info.fetch_children_flaky = False
                raise PeerRequestException
            else:
                return await func(coin_name, peer, fork_height)

        return new_func
```
