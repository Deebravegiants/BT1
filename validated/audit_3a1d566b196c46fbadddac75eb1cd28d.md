### Title
Unconditional Cache Population on Failed Merkle Proof Allows Phantom Coin Injection into Wallet State — (File: `chia/wallet/util/wallet_sync_utils.py`)

### Summary
In `request_and_validate_additions`, the per-peer additions cache is populated unconditionally even when `validate_additions` returns `False`. A subsequent call for the same `(header_hash, puzzle_hash)` pair returns `True` from cache without re-validating. Because the per-peer cache is never evicted on disconnect, an attacker controlling a full node can poison the cache on a first connection, reconnect with the same node ID, and have the wallet accept fabricated coin states as Merkle-proven — injecting phantom coins into the wallet's coin store.

### Finding Description

`request_and_validate_additions` in `chia/wallet/util/wallet_sync_utils.py` contains the following sequence:

```python
result: bool = validate_additions(
    additions_res.coins,
    additions_res.proofs,
    additions_root,
)
peer_request_cache.add_to_additions_in_block(header_hash, puzzle_hash, height)  # unconditional
return result
``` [1](#0-0) 

`add_to_additions_in_block` is called regardless of whether `result` is `True` or `False`. The cache check at the top of the same function short-circuits to `True` on any subsequent call for the same key:

```python
if peer_request_cache.in_additions_in_block(header_hash, puzzle_hash):
    return True
``` [2](#0-1) 

The `PeerRequestCache` is stored in `WalletNode.peer_caches`, a `dict[bytes32, PeerRequestCache]` keyed by `peer_node_id`:

```python
def get_cache_for_peer(self, peer: WSChiaConnection) -> PeerRequestCache:
    if peer.peer_node_id not in self.peer_caches:
        self.peer_caches[peer.peer_node_id] = PeerRequestCache()
    return self.peer_caches[peer.peer_node_id]
``` [3](#0-2) 

There is no eviction of `peer_caches` entries on peer disconnect (confirmed: no `peer_caches.pop` or equivalent exists in `wallet_node.py`). A reconnecting peer with the same node ID reuses the same `PeerRequestCache` instance, including any poisoned entries. [4](#0-3) 

### Impact Explanation

When `validate_additions_result is False`, `validate_received_state_from_peer` closes the peer and returns `False`:

```python
if validate_additions_result is False:
    self.log.warning("Validate false 1")
    await peer.close(9999)
    return False
``` [5](#0-4) 

However, the cache entry `(header_hash, puzzle_hash)` was already written. On reconnection with the same `peer_node_id`, any coin state whose puzzle hash and creation block match the poisoned cache entry bypasses Merkle proof verification entirely and is accepted as valid. The wallet then calls `wallet_state_manager.add_coin_states` with the fabricated state, corrupting the coin store with phantom coins the wallet does not actually own on-chain. [6](#0-5) 

### Likelihood Explanation

The attacker only needs to operate a full node that the wallet connects to — a standard untrusted peer. No keys, admin access, or cryptographic break is required. The wallet connects to untrusted peers by design during sync. The two-step exploit (connect → poison cache → disconnect → reconnect → inject) is straightforward for any node operator.

### Recommendation

Condition the cache write on a successful validation result:

```python
result: bool = validate_additions(
    additions_res.coins,
    additions_res.proofs,
    additions_root,
)
if result:
    peer_request_cache.add_to_additions_in_block(header_hash, puzzle_hash, height)
return result
```

Additionally, evict the per-peer `PeerRequestCache` from `peer_caches` when a peer disconnects, to prevent stale or poisoned cache entries from persisting across reconnections. [7](#0-6) 

### Proof of Concept

1. Attacker operates a full node; wallet connects to it (untrusted peer, normal operation).
2. Attacker sends a `CoinStateUpdate` claiming coin `C` with `puzzle_hash=PH` was created at block `B` (header hash `HH`).
3. Wallet calls `request_and_validate_additions(peer, cache, height=B, header_hash=HH, puzzle_hash=PH, additions_root=R)`.
4. Attacker's node responds with a `RespondAdditions` carrying a structurally valid but cryptographically incorrect Merkle proof. `validate_additions` returns `False`.
5. **Bug fires:** `peer_request_cache.add_to_additions_in_block(HH, PH, B)` is called unconditionally. Cache entry `(HH, PH)` is now marked as "validated."
6. `validate_received_state_from_peer` closes the peer and returns `False`.
7. Attacker reconnects with the same node ID (same keypair → same `peer_node_id`). `get_cache_for_peer` returns the existing poisoned `PeerRequestCache`.
8. Attacker sends a new `CoinStateUpdate` for coin `C'` (arbitrary amount, same `puzzle_hash=PH`, same block `B`).
9. Wallet calls `request_and_validate_additions` → cache hit on `(HH, PH)` → returns `True` immediately, no network request made, no proof verified.
10. `validate_received_state_from_peer` returns `True`. `add_coin_states` writes `C'` into the wallet's coin store.
11. Wallet now shows a phantom balance for a coin that does not exist on-chain. [2](#0-1) [8](#0-7)

### Citations

**File:** chia/wallet/util/wallet_sync_utils.py (L197-224)
```python
async def request_and_validate_additions(
    peer: WSChiaConnection,
    peer_request_cache: PeerRequestCache,
    height: uint32,
    header_hash: bytes32,
    puzzle_hash: bytes32,
    additions_root: bytes32,
) -> bool | None:
    if peer_request_cache.in_additions_in_block(header_hash, puzzle_hash):
        return True
    additions_request = RequestAdditions(height, header_hash, [puzzle_hash])
    additions_res: RespondAdditions | RejectAdditionsRequest | None = await peer.call_api(
        FullNodeAPI.request_additions, additions_request
    )
    if additions_res is None or isinstance(additions_res, RejectAdditionsRequest):
        log.info(
            f"Failed to obtain additions for height {height} header hash {header_hash} "
            f"puzzle hash {puzzle_hash} from peer {peer.peer_node_id} / {peer.peer_info.host} "
            f"version {peer.version} response: {additions_res}"
        )
        return None
    result: bool = validate_additions(
        additions_res.coins,
        additions_res.proofs,
        additions_root,
    )
    peer_request_cache.add_to_additions_in_block(header_hash, puzzle_hash, height)
    return result
```

**File:** chia/wallet/wallet_node.py (L160-160)
```python
    peer_caches: dict[bytes32, PeerRequestCache] = dataclasses.field(default_factory=dict)
```

**File:** chia/wallet/wallet_node.py (L234-237)
```python
    def get_cache_for_peer(self, peer: WSChiaConnection) -> PeerRequestCache:
        if peer.peer_node_id not in self.peer_caches:
            self.peer_caches[peer.peer_node_id] = PeerRequestCache()
        return self.peer_caches[peer.peer_node_id]
```

**File:** chia/wallet/wallet_node.py (L1016-1023)
```python
                    valid_states = await self._collect_valid_states(inner_states, peer, cache, fork_height)
                    if len(valid_states) > 0:
                        async with self.wallet_state_manager.db_wrapper.writer():
                            self.log.info(
                                f"new coin state received ({inner_idx_start}-"
                                f"{inner_idx_start + len(inner_states) - 1}/ {len(updated_coin_states)})"
                            )
                            await self.wallet_state_manager.add_coin_states(valid_states, peer, fork_height)
```

**File:** chia/wallet/wallet_node.py (L1575-1578)
```python
        if validate_additions_result is False:
            self.log.warning("Validate false 1")
            await peer.close(9999)
            return False
```

**File:** chia/wallet/util/peer_request_cache.py (L88-92)
```python
    def add_to_additions_in_block(self, header_hash: bytes32, addition_ph: bytes32, height: uint32) -> None:
        self._additions_in_block.put((header_hash, addition_ph), height)

    def in_additions_in_block(self, header_hash: bytes32, addition_ph: bytes32) -> bool:
        return self._additions_in_block.get((header_hash, addition_ph)) is not None
```
