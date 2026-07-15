### Title
Silent Coin Drop via Malicious Peer Returning Mismatched Parent `spent_height` in `determine_coin_type` — (`chia/wallet/wallet_state_manager.py`)

### Summary

An unprivileged remote peer (a full node the wallet connects to) can cause the wallet to permanently and silently skip recording a received coin by returning a parent `CoinState` with a `spent_height` that does not equal the child coin's `created_height`. This triggers an `AssertionError` inside `determine_coin_type`, which is caught by the broad `except Exception` handler in `_add_coin_states`. Because `AssertionError` is not a `PeerRequestException` or `aiosqlite.Error`, the coin is removed from the retry store and silently dropped — never recorded in the wallet's coin store.

### Finding Description

**Call sequence:**

1. `_add_coin_states` iterates over incoming `coin_states` from a peer.
2. For a new coin whose puzzle hash is unrecognized and whose parent is not in the local DB, the branch at line 1828–1829 is taken: [1](#0-0) 

3. `determine_coin_type` calls `get_coin_state([parent_coin_info])` on the peer to fetch the parent's state.
4. The peer (attacker-controlled) returns a `CoinState` for the parent where `spent_height != coin_state.created_height`.
5. The `assert parent_coin_state.spent_height == coin_state.created_height` inside `determine_coin_type` fires, raising `AssertionError`.
6. The exception propagates to the outer handler in `_add_coin_states`: [2](#0-1) 

7. The handler checks `isinstance(e, (PeerRequestException, aiosqlite.Error))` — `AssertionError` matches neither, so the `else` branch executes `retry_store.remove_state(coin_state)` and `continue`. The coin is **permanently dropped**.

**The critical flaw** is the exception triage at lines 2231–2234: only network/DB errors trigger a retry. Any other exception — including `AssertionError` from a peer-supplied bad value — causes the coin to be silently discarded with no retry and no user-visible error. [3](#0-2) 

### Impact Explanation

- The wallet fails to record a coin it owns (XCH, CAT, NFT, DID, VC, pool singleton child, etc.).
- The wallet balance is permanently understated for that coin.
- For CAT/NFT/DID coins, the wallet never creates the corresponding wallet object, so the asset is invisible to the user.
- The coin is removed from the retry store, so no subsequent sync attempt will recover it unless the wallet performs a full resync.

This maps directly to the allowed High impact: **"Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact."**

### Likelihood Explanation

- Any peer the wallet connects to (trusted or untrusted) can trigger this. In Chia, wallets routinely connect to public full nodes.
- The attacker only needs to serve a crafted response to `get_coin_state` for the parent coin — a single malformed field (`spent_height`) is sufficient.
- No key material, admin access, or cryptographic break is required.
- The attack is silent: no exception is surfaced to the user, only a log line at `exception` level.

### Recommendation

1. **Triage `AssertionError` as a retryable error** (or at minimum, do not remove from retry store): treat any exception from `determine_coin_type` that originates from a peer-supplied value as a peer fault, not a permanent local failure.
2. **Replace the bare `assert` in `determine_coin_type`** with an explicit `raise ValueError(...)` or `raise PeerRequestException(...)` so the exception type correctly signals a peer protocol violation and triggers the retry path.
3. **Validate peer responses** before using them in assertions: check `parent_coin_state.spent_height == coin_state.created_height` with an explicit conditional and raise a typed exception rather than relying on `assert`.

### Proof of Concept

```python
# Mock get_coin_state on the peer to return a parent with wrong spent_height
# e.g., coin_state.created_height = 100, but parent.spent_height = 99

async def mock_get_coin_state(coin_ids, peer, fork_height):
    parent = CoinState(
        coin=parent_coin,
        spent_height=uint32(99),   # should be 100 to match coin_state.created_height
        created_height=uint32(50),
    )
    return [parent]

# Patch wallet_node.get_coin_state with mock_get_coin_state
# Call _add_coin_states with a coin_state for a CAT coin (created_height=100, parent not in DB)
# Assert: coin is NOT in coin_store after the call (silently dropped)
# Assert: coin is NOT in retry_store (permanently lost)
```

The test would confirm the coin is neither recorded nor retried — it is silently discarded.

### Citations

**File:** chia/wallet/wallet_state_manager.py (L1828-1829)
```python
                    elif coin_state.created_height is not None:
                        wallet_identifier, coin_data = await self.determine_coin_type(peer, coin_state, fork_height)
```

**File:** chia/wallet/wallet_state_manager.py (L2227-2235)
```python
            except Exception as e:
                self.log.exception(f"Failed to add coin_state: {coin_state}, error: {e}")
                if rollback_wallets is not None:
                    self.wallets = rollback_wallets  # Restore since DB will be rolled back by writer
                if isinstance(e, (PeerRequestException, aiosqlite.Error)):
                    await self.retry_store.add_state(coin_state, peer.peer_node_id, fork_height)
                else:
                    await self.retry_store.remove_state(coin_state)
                continue
```
