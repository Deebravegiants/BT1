Looking at the actual code carefully to trace the full attack path.

**Key code in `validate_removals` (proofs=None branch):** [1](#0-0) 

When `proofs is None`, the function builds `removals_items` by filtering out entries where `coin is None`. It then computes the Merkle root of only the non-None entries and compares to the block's `removals_root`. **It never checks that the specific queried coin is actually present in the removals set.**

**The caller never checks either:** [2](#0-1) 

`request_and_validate_removals` passes `coin_name` to identify which coin to verify, but just forwards the raw `validate_removals` result — which only checks set-root consistency, not coin-specific inclusion.

**The wallet trusts this result:** [3](#0-2) 

If `validate_removals_result` is `True`, the wallet proceeds to accept the spent state.

---

**Concrete attack path:**

1. Attacker operates a malicious peer.
2. Attacker identifies coin_A owned by the victim wallet (observable on-chain).
3. Attacker finds any block H with no transactions — its `removals_root = compute_merkle_set_root([])` (the empty Merkle root, a fixed known value).
4. Attacker sends `CoinState(coin=coin_A, created_height=H_create, spent_height=H)`.
5. Wallet calls `validate_received_state_from_peer`:
   - Additions check at `H_create` passes (coin_A was genuinely created).
   - Wallet calls `request_and_validate_removals(peer, H, header_hash, coin_A.name(), empty_root)`.
6. Malicious peer returns `RespondRemovals(coins=[(coin_A.name(), None)], proofs=None)`.
7. `validate_removals` computes `removals_items = []` (coin_A excluded because `coin is None`), then `compute_merkle_set_root([]) == empty_root` → returns `True`.
8. `validate_block_inclusion` passes because block H is a real, valid block in the chain.
9. Wallet marks coin_A as spent — **permanently corrupting its coin records**.

---

**Why existing guards don't stop this:**

- `validate_block_inclusion` only verifies the block header is in the chain via the weight proof — it does not verify that coin_A is in the block's removals set.
- The `proofs=None` branch of `validate_removals` is designed to verify the entire removals set by root, but silently skips `coin=None` entries without checking that the queried coin appears with a non-None object.
- There is no post-check in `request_and_validate_removals` or `validate_received_state_from_peer` that asserts coin_A.name() was found with a non-None coin in the response.

---

### Title
`validate_removals` silently excludes `coin=None` entries from Merkle root check, allowing a malicious peer to falsely confirm a coin as spent — (`chia/wallet/util/wallet_sync_utils.py`)

### Summary
`validate_removals` with `proofs=None` builds the Merkle root only from entries where `coin is not None`. A malicious peer can return `(coin_A.name(), None)` for the queried coin, causing it to be excluded from the root computation. If the block's `removals_root` equals `compute_merkle_set_root([])` (any block with no transactions), validation returns `True` despite coin_A not being in the removals set.

### Finding Description
In `validate_removals` at line 138:

```python
removals_items = [name for name, coin in coins if coin is not None]
```

When `proofs=None`, the protocol semantics are that the full node returns all removals, with `coin=None` meaning the coin was **not** removed. The function correctly excludes these from the root computation — but never asserts that the specific coin being queried appears with a non-None object. The caller `request_and_validate_removals` passes `coin_name` as the coin to verify but does not check that it appears as `(coin_name, non_None_coin)` in the response. A malicious peer can return `(coin_name, None)` and, if the block has an empty removals root, the validation passes.

### Impact Explanation
The wallet permanently marks an unspent coin as spent. The user's balance is reduced by the coin's value, and the wallet will not attempt to spend the coin (believing it already spent). This constitutes **corruption of coin records with direct security impact** — the user loses access to funds they still own on-chain.

### Likelihood Explanation
Any unprivileged peer the wallet connects to can execute this attack. The attacker only needs to: (a) know a coin owned by the victim (observable on-chain), and (b) identify any block with no transactions (common on mainnet). No keys, admin access, or cryptographic breaks are required.

### Recommendation
After `validate_removals` returns `True` with `proofs=None`, verify that the queried `coin_name` appears in the response with a non-None coin object:

```python
# In request_and_validate_removals, after validate_removals returns True:
coin_map = dict(removals_res.coins)
if coin_map.get(coin_name) is None:
    return False  # coin not confirmed as removed
```

Alternatively, fix `validate_removals` to accept the expected coin name and assert its presence.

### Proof of Concept

```python
from chia_rs import compute_merkle_set_root
from chia.wallet.util.wallet_sync_utils import validate_removals

# Any block with no transactions has this removals root
empty_root = bytes32(compute_merkle_set_root([]))

# Peer returns (coin_A.name(), None) — claiming coin_A was NOT removed
coins = [(coin_A.name(), None)]

# validate_removals returns True despite coin_A not being in the removals set
result = validate_removals(coins, None, empty_root)
assert result is True  # BUG: should be False
```

The wallet then calls `validate_block_inclusion` on a real empty-transaction block (which passes), and proceeds to mark coin_A as spent.

#Vulnerability found.

### Citations

**File:** chia/wallet/util/wallet_sync_utils.py (L133-141)
```python
    if proofs is None:
        # If there are no proofs, it means all removals were returned in the response.
        # we must find the ones relevant to our wallets.

        # Verify removals root
        removals_items = [name for name, coin in coins if coin is not None]
        removals_root = bytes32(compute_merkle_set_root(removals_items))
        if root != removals_root:
            return False
```

**File:** chia/wallet/util/wallet_sync_utils.py (L175-194)
```python
async def request_and_validate_removals(
    peer: WSChiaConnection, height: uint32, header_hash: bytes32, coin_name: bytes32, removals_root: bytes32
) -> bool | None:
    """
    Returns None on failure to obtain removals, otherwise it returns True or
    False depending on the outcome of validation.
    """
    removals_request = RequestRemovals(height, header_hash, [coin_name])

    removals_res: RespondRemovals | RejectRemovalsRequest | None = await peer.call_api(
        FullNodeAPI.request_removals, removals_request
    )
    if removals_res is None or isinstance(removals_res, RejectRemovalsRequest):
        log.info(
            f"Failed to obtain removals for height {height} header hash {header_hash} "
            f"coin name {coin_name} from peer {peer.peer_node_id} / {peer.peer_info.host} "
            f"version {peer.version} response: {removals_res}"
        )
        return None
    return validate_removals(removals_res.coins, removals_res.proofs, removals_root)
```

**File:** chia/wallet/wallet_node.py (L1626-1642)
```python
            validate_removals_result = await request_and_validate_removals(
                peer,
                spent_state_block.height,
                spent_state_block.header_hash,
                coin_state.coin.name(),
                spent_state_block.foliage_transaction_block.removals_root,
            )
            if validate_removals_result is None:
                return False
            if validate_removals_result is False:
                self.log.warning("Validate false 3")
                await peer.close(9999)
                return False
            validated = await self.validate_block_inclusion(spent_state_block, peer, peer_request_cache)
            if not validated:
                return False
        peer_request_cache.add_to_states_validated(coin_state)
```
