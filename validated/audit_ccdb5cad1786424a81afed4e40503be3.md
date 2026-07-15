The code trace is complete. Let me lay out the exact findings.

## Full Attack Path Trace

**Entry**: `WalletNodeAPI.new_peak_wallet` → `new_peak_queue` → `WalletNode.new_peak_wallet`

**Guards in `new_peak_wallet`** (lines 1197–1238):
- Weight check: `new_peak.weight < peak_hb.weight` → attacker sets weight > current peak (no cryptographic binding)
- Header hash consistency: wallet fetches `RequestBlockHeader(height)` from the peer and checks `new_peak_hb.header_hash == new_peak.header_hash` — attacker controls both sides
- Timestamp check: `is_timestamp_in_sync(timestamp)` — attacker sets `foliage_transaction_block.timestamp ≈ time.time()` in the fabricated block

**Critical branch in `new_peak_from_untrusted`** (line 1279):

```python
if new_peak_hb.height < self.constants.WEIGHT_PROOF_RECENT_BLOCKS:
    return await self.sync_from_untrusted_close_to_peak(new_peak_hb, peer)
```

`WEIGHT_PROOF_RECENT_BLOCKS = 1000` on mainnet. For any claimed height < 1000, weight proof validation is **entirely skipped** and `sync_from_untrusted_close_to_peak` is called directly.

**Inside `wallet_short_sync_backtrack`** (lines 1393–1456):

The cap guard (line 1408–1417):
```python
if (
    peak_hb is not None
    and len(blocks) > self.LONG_SYNC_THRESHOLD   # 300
    and header_block.height >= self.constants.WEIGHT_PROOF_RECENT_BLOCKS  # 1000
):
    return None
```
With `header_block.height < 1000`, the third condition is **always False** — the cap never fires regardless of how many blocks are walked back.

The chain continuity check (line 1425):
```python
if prev_head.header_hash != top.prev_header_hash:
    await peer.close()
    return None
```
This only verifies internal hash-chain consistency. The attacker controls all served blocks and can trivially construct a chain where each block's `header_hash` (computed from attacker-controlled content) matches the next block's `prev_header_hash`. This does **not** verify the chain is canonical.

**Rollback before validation** (lines 1438–1454):
```python
if top.height == 0:
    fork_height = 0
    should_skip_rollback = peak_hb is None   # False when wallet has state

peak_height = await self.wallet_state_manager.blockchain.get_finished_sync_up_to()
if not should_skip_rollback and fork_height < peak_height:
    await self.perform_atomic_rollback(fork_height)   # ← WIPES STATE
    await self.update_ui()

for block in blocks:
    res, err = await self.wallet_state_manager.blockchain.add_block(block)
    if res == AddBlockResult.INVALID_BLOCK:
        raise ValueError(err)   # ← too late, rollback already committed
```

`perform_atomic_rollback(0)` is called **before** `add_block` validates any block. Even if every fabricated block fails `validate_finished_header_block` (VDF/PoSpace checks), the rollback is already committed to the DB.

**`WalletBlockchain.add_block`** (lines 105–135) does call `validate_finished_header_block` with full VDF/PoSpace validation. Fabricated blocks will fail. But the `reorg_rollback(0)` and `set_finished_sync_up_to(0)` have already executed inside `perform_atomic_rollback`.

**`on_connect` guard** (line 807–808):
```python
if not trusted and self.local_node_synced:
    await peer.close()
```
`local_node_synced` is only True when a trusted peer is connected and synced. Wallets without a configured trusted peer (the common case for light wallets) are fully exposed.

---

### Title
Untrusted peer can trigger `perform_atomic_rollback(0)` without weight proof, wiping wallet sync state — (`chia/wallet/wallet_node.py`)

### Summary
An untrusted peer can force `perform_atomic_rollback(0)` on a wallet with existing state by advertising a fabricated chain of height < `WEIGHT_PROOF_RECENT_BLOCKS` (1000). The rollback executes before any block validation, so invalid fabricated blocks still cause the erasure.

### Finding Description
`new_peak_from_untrusted` unconditionally bypasses weight proof validation for any claimed peak height < 1000 (line 1279). [1](#0-0)  Inside `wallet_short_sync_backtrack`, the `LONG_SYNC_THRESHOLD` cap requires `header_block.height >= WEIGHT_PROOF_RECENT_BLOCKS` to fire, so it is permanently disabled for the same height range. [2](#0-1)  The chain continuity check only verifies internal hash-chain consistency, not canonical chain membership. [3](#0-2)  When the backtrack reaches genesis with `peak_hb is not None`, `should_skip_rollback = False` and `perform_atomic_rollback(0)` is called unconditionally before any block is passed to `WalletBlockchain.add_block`. [4](#0-3)  `WalletBlockchain.add_block` does call `validate_finished_header_block` with full VDF/PoSpace checks, but this happens after the rollback is already committed. [5](#0-4) 

### Impact Explanation
`perform_atomic_rollback(0)` calls `reorg_rollback(0)` and `set_finished_sync_up_to(0)`, erasing all coin records, transaction history, and sync progress above height 0. [6](#0-5)  The wallet shows zero balance and must re-sync from scratch. During the re-sync window the wallet cannot correctly report balances or detect incoming/outgoing transactions, which can cause financial decisions based on incorrect state. The own developers acknowledge this behavior in test comments: [7](#0-6) 

### Likelihood Explanation
Any peer the wallet connects to (discovered via DNS introducers or peer exchange) can execute this. The only mitigation is `local_node_synced`, which is False whenever no trusted synced peer is connected — the default for light wallets. The attack requires no keys, no PoW, and no valid blocks; only a TCP connection and the ability to serve fabricated `RespondBlockHeader` responses.

### Recommendation
Move `perform_atomic_rollback` to after all blocks have been successfully validated by `add_block`, or require weight proof validation before any rollback for untrusted peers regardless of chain height. The existing cap guard should also be restructured so that `header_block.height < WEIGHT_PROOF_RECENT_BLOCKS` does not disable it when `peak_hb is not None`.

### Proof of Concept
1. Run a malicious full node that responds to `RequestBlockHeader(h)` with a fabricated `HeaderBlock` at height `h`, where each block's `prev_header_hash` equals the hash of the block served at height `h-1` (trivial hash chain), and the block at height 999 has `foliage_transaction_block.timestamp ≈ time.time()`.
2. Connect to a wallet that has existing state (synced to any height > 0) and no trusted peer.
3. Send `NewPeakWallet(header_hash=H_999, height=999, weight=HUGE, fork_point=0)`.
4. Serve the fabricated chain for all subsequent `RequestBlockHeader` calls.
5. Observe `perform_atomic_rollback(0)` is called (loggable), wallet balance drops to 0, and `get_finished_sync_up_to()` returns 0.
6. The subsequent `add_block` calls raise `ValueError` (fabricated blocks fail VDF validation), but the rollback is already committed.

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

**File:** chia/wallet/wallet_blockchain.py (L123-133)
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
```

**File:** chia/_tests/wallet/test_wallet_node.py (L1066-1070)
```python
    # TODO, there is a bug in wallet_short_sync_backtrack which leads to a rollback to 0 (-1 which is another a bug) and
    #       with that to a KeyError when applying the race cache if there are less than WEIGHT_PROOF_RECENT_BLOCKS
    #       blocks but we still have a peak stored in the DB. So we need to add enough blocks for a weight proof here to
    #       be able to restart the wallet in this test.
    await add_blocks_in_batches(default_1000_blocks[:600], full_node_api.full_node)
```
