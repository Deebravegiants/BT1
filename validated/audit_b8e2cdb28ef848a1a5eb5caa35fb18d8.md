The claim is substantiated by the code. Let me trace the exact path.

### Title
Untrusted Peer Can Force Full Wallet State Erasure via Fabricated Short-Chain Backtrack — (`chia/wallet/wallet_node.py`)

### Summary

An untrusted peer can trigger `perform_atomic_rollback(0)` — wiping all wallet coin records, transactions, and sync state — by serving a fabricated chain of `HeaderBlock`s with height below `WEIGHT_PROOF_RECENT_BLOCKS`. The rollback is committed to the database **before** `add_block` validates the blocks, so even though the fabricated blocks subsequently fail VDF validation, the damage is already done.

---

### Finding Description

**Entrypoint**: `new_peak_wallet` → `new_peak_from_untrusted` → `sync_from_untrusted_close_to_peak` → `wallet_short_sync_backtrack`

**Step 1 — Weight proof bypass for short chains.**

In `new_peak_from_untrusted`, when the announced height is below `WEIGHT_PROOF_RECENT_BLOCKS`, the code skips weight proof validation entirely and goes directly to `sync_from_untrusted_close_to_peak`: [1](#0-0) 

No cryptographic validation of the peer's claimed weight occurs on this path.

**Step 2 — Backtrack cap is disabled for short chains.**

Inside `wallet_short_sync_backtrack`, the cap that would abort the backtrack and redirect to long sync only fires when `header_block.height >= WEIGHT_PROOF_RECENT_BLOCKS`: [2](#0-1) 

For a chain with `height < WEIGHT_PROOF_RECENT_BLOCKS`, the third condition is always `False`, so the cap never triggers regardless of how many blocks the attacker serves.

**Step 3 — Chain continuity check is not a barrier.**

The only per-block check during backtrack is that each fetched block's `header_hash` matches the requesting block's `prev_header_hash`: [3](#0-2) 

This validates internal chain consistency only. The attacker pre-computes a chain of fabricated `HeaderBlock`s where each block's `header_hash` is set to the next block's `prev_header_hash`. This passes trivially.

**Step 4 — Rollback fires before block validation.**

When the backtrack reaches genesis (`top.height == 0`) and the wallet has existing state (`peak_hb is not None`), `should_skip_rollback` is set to `False`: [4](#0-3) 

`perform_atomic_rollback(0)` is called and committed to the database at line 1447. Only **after** this does the code attempt to add the attacker's blocks via `add_block`: [5](#0-4) 

`WalletBlockchain.add_block` calls `validate_finished_header_block` with full VDF proof checking: [6](#0-5) 

The fabricated blocks fail VDF validation and return `INVALID_BLOCK`, raising a `ValueError`. But the rollback is already committed. The wallet state is permanently wiped until a full re-sync.

**Step 5 — Timestamp guard is not a barrier.**

The `is_timestamp_in_sync` check at line 1232 reads a timestamp from a `HeaderBlock` fetched from the peer: [7](#0-6) 

The attacker controls the `HeaderBlock` response and can set `foliage_transaction_block.timestamp` to any recent value. The timestamp is not cryptographically validated at this point.

**Violated invariant.** The code comment in `add_states_from_peer` explicitly states the invariant that is broken: [8](#0-7) 

> "wallet_short_sync_backtrack can safely rollback because we validated the weight for the new peak so we know the peer is telling the truth about the reorg."

This invariant does not hold for `height < WEIGHT_PROOF_RECENT_BLOCKS`.

---

### Impact Explanation

`perform_atomic_rollback(0)` calls `reorg_rollback(0)` which erases all wallet coin records, transaction history, and sync state, then sets `finished_sync_up_to = 0`: [9](#0-8) 

Consequences:
- All confirmed and unconfirmed coin records are erased from the wallet DB
- All pending transactions (offers, DID/NFT operations, clawbacks, pool actions) are lost
- The wallet must re-sync from scratch; unconfirmed transactions are permanently lost
- The attack is repeatable: the attacker can re-trigger it every time the wallet re-syncs

This maps to: **High — Corruption of wallet sync state, coin records, and offer/trade settlement state with direct security impact.**

---

### Likelihood Explanation

- Requires only a standard untrusted peer connection (no keys, no admin access)
- The attacker needs to serve at most `WEIGHT_PROOF_RECENT_BLOCKS` fabricated `HeaderBlock`s (~1000 on mainnet) with pre-computed hash links — trivial to construct
- The fabricated `NewPeakWallet` weight just needs to exceed the wallet's current peak weight (a single integer field)
- No cryptographic material needs to be forged to reach the rollback; VDF forgery is only needed for `add_block`, which runs after the damage is done

---

### Recommendation

1. **Do not call `perform_atomic_rollback` before block validation.** Validate all blocks in the attacker-supplied chain first; only roll back if all blocks pass `add_block` successfully.
2. **Require weight proof validation before any rollback on untrusted paths**, even for `height < WEIGHT_PROOF_RECENT_BLOCKS`. If a weight proof cannot be produced for a short chain, treat the peer as untrusted and do not roll back.
3. **Alternatively**, make the rollback and block addition atomic: wrap both in a single DB transaction so that a failed `add_block` automatically reverts the rollback.

---

### Proof of Concept

```python
# Attacker constructs a chain of N+1 fabricated HeaderBlocks (N < WEIGHT_PROOF_RECENT_BLOCKS)
# Each block's header_hash is set to the next block's prev_header_hash (valid hash links)
# The tip block claims weight > wallet's current peak weight

# 1. Connect untrusted peer to wallet
# 2. Send NewPeakWallet(header_hash=H_N, height=N, weight=HUGE, fork_point=0)
# 3. Respond to RequestBlockHeader(N) with fabricated HeaderBlock at height N
#    (header_hash=H_N, weight=HUGE, foliage_transaction_block.timestamp=now)
# 4. For each RequestBlockHeader(h) in the backtrack loop (h = N-1 down to 0):
#    respond with fabricated HeaderBlock where header_hash=H_h, prev_header_hash=H_{h+1}
# 5. wallet_short_sync_backtrack reaches height 0, peak_hb is not None
#    → should_skip_rollback = False, fork_height = 0
#    → perform_atomic_rollback(0) fires → wallet DB wiped
# 6. add_block(fabricated_genesis) → INVALID_BLOCK (VDF fails) → ValueError raised
#    → rollback already committed, wallet state gone

# Assert: wallet coin records, tx history, and finished_sync_up_to are all reset to 0
```

### Citations

**File:** chia/wallet/wallet_node.py (L826-845)
```python
    async def perform_atomic_rollback(self, fork_height: int, cache: PeerRequestCache | None = None) -> None:
        self.log.info(f"perform_atomic_rollback to {fork_height}")
        # this is to start a write transaction
        async with self.wallet_state_manager.db_wrapper.writer():
            try:
                removed_wallet_ids = await self.wallet_state_manager.reorg_rollback(fork_height)
                await self.wallet_state_manager.blockchain.set_finished_sync_up_to(fork_height, in_rollback=True)
                if cache is None:
                    self.rollback_request_caches(fork_height)
                else:
                    cache.clear_after_height(fork_height)
            except Exception as e:
                tb = traceback.format_exc()
                self.log.error(f"Exception while perform_atomic_rollback: {e} {tb}")
                raise
            else:
                await self.wallet_state_manager.blockchain.clean_block_records()

                for wallet_id in removed_wallet_ids:
                    self.wallet_state_manager.wallets.pop(wallet_id)
```

**File:** chia/wallet/wallet_node.py (L1231-1238)
```python
        latest_timestamp = await self.get_timestamp_for_height_from_peer(new_peak_hb.height, peer)
        if latest_timestamp is None or not self.is_timestamp_in_sync(latest_timestamp):
            if trusted:
                self.log.debug(f"Trusted peer {peer.get_peer_info()} is not synced.")
            else:
                self.log.warning(f"Non-trusted peer {peer.get_peer_info()} is not synced, disconnecting")
                await peer.close(120)
            return
```

**File:** chia/wallet/wallet_node.py (L1279-1281)
```python
        if new_peak_hb.height < self.constants.WEIGHT_PROOF_RECENT_BLOCKS:
            # this is the case happens chain is shorter then WEIGHT_PROOF_RECENT_BLOCKS
            return await self.sync_from_untrusted_close_to_peak(new_peak_hb, peer)
```

**File:** chia/wallet/wallet_node.py (L1408-1417)
```python
            if (
                peak_hb is not None
                and len(blocks) > self.LONG_SYNC_THRESHOLD
                and header_block.height >= self.constants.WEIGHT_PROOF_RECENT_BLOCKS
            ):
                self.log.info(
                    f"Backtrack exceeded {self.LONG_SYNC_THRESHOLD} headers at height "
                    f"{header_block.height}, switching to long sync for peer {peer.peer_info.host}"
                )
                return None
```

**File:** chia/wallet/wallet_node.py (L1425-1431)
```python
            if prev_head.header_hash != top.prev_header_hash:
                self.log.warning(
                    f"Backtrack chain discontinuity at height {prev_head.height}, "
                    f"disconnecting peer {peer.peer_info.host}"
                )
                await peer.close()
                return None
```

**File:** chia/wallet/wallet_node.py (L1438-1448)
```python
        if top.height == 0:
            fork_height = 0
            should_skip_rollback = peak_hb is None

        # Roll back coins and transactions
        peak_height = await self.wallet_state_manager.blockchain.get_finished_sync_up_to()
        if not should_skip_rollback and fork_height < peak_height:
            self.log.info(f"Rolling back to {fork_height}")
            # we should clear all peers since this is a full rollback
            await self.perform_atomic_rollback(fork_height)
            await self.update_ui()
```

**File:** chia/wallet/wallet_node.py (L1450-1454)
```python
        for block in blocks:
            # Set blockchain to the latest peak
            res, err = await self.wallet_state_manager.blockchain.add_block(block)
            if res == AddBlockResult.INVALID_BLOCK:
                raise ValueError(err)
```

**File:** chia/wallet/wallet_node.py (L1976-1979)
```python

```

**File:** chia/wallet/wallet_blockchain.py (L123-135)
```python
        required_iters, error = validate_finished_header_block(
            self.constants,
            self,
            block,
            False,
            expected_vs,
            check_sub_epoch_summary=False,
            skip_commitment_validation=True,
        )
        if error is not None:
            return AddBlockResult.INVALID_BLOCK, error.code
        if required_iters is None:
            return AddBlockResult.INVALID_BLOCK, Err.INVALID_POSPACE
```
