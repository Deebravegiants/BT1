Let me look at the exact code flow more carefully to confirm the vulnerability.

The vulnerability is real and concrete. Let me trace the exact code path:

**Step 1 — `add_prevalidated_blocks` iterates the batch and commits blocks to DB**

For each block at position `i = 0..K-1`, `self.blockchain.add_block()` is called and commits the block to the DB. When `result == AddBlockResult.NEW_PEAK`, the per-block `state_change_summary` is accumulated into `agg_state_change_summary`. [1](#0-0) 

**Step 2 — At block K, an error is detected and the function returns early with BOTH summary and error**

If `pre_validation_results[K].error is not None`, the function returns `(agg_state_change_summary, Err(...))` — the accumulated summary for blocks 0..K-1 is non-None, and the error is non-None simultaneously. [2](#0-1) 

Same early return path for `INVALID_BLOCK`/`DISCONNECTED_BLOCK` at block K: [3](#0-2) 

**Step 3 — `ingest_batch` checks `err is not None` first and raises before calling `hint_store.add_hints`**

The `if err is not None` branch bans the peer and raises `ValueError`. The `hint_store.add_hints` call at line 1437 is never reached, even though `state_change_summary` is non-None and contains hints for the K already-committed blocks. [4](#0-3) 

**Step 4 — The corruption is permanent**

On re-sync from a different peer, `blockchain.add_block` returns `ALREADY_HAVE_BLOCK` for blocks 0..K-1, so `agg_state_change_summary` is never populated for them, and `hint_store.add_hints` is never called. There is no recovery path.

**Step 5 — Impact on wallets**

`register_for_ph_updates` uses `hint_store.get_coin_ids_multi` to find hinted coins for wallets. Missing hints mean wallets permanently miss incoming hinted payments (CATs, NFTs, DID operations, offer settlements — all of which use the `CREATE_COIN` hint mechanism). [5](#0-4) 

---

### Title
Malicious Sync Peer Causes Permanent Hint Index Corruption via Mixed-Validity Batch — (`chia/full_node/full_node.py`)

### Summary
During `sync_from_fork_point`, a malicious peer can send a batch where blocks 0..K-1 are valid (committed to the coin DB) and block K is invalid. `add_prevalidated_blocks` returns `(agg_state_change_summary, error)` with both fields non-None. `ingest_batch` raises `ValueError` on the error before calling `hint_store.add_hints`, permanently omitting hints for all coins created in blocks 0..K-1.

### Finding Description
`add_prevalidated_blocks` accumulates `agg_state_change_summary` as it commits blocks to the DB one by one. On encountering an invalid block at position K, it returns the partially-accumulated summary alongside the error (lines 1692, 1749). In `ingest_batch`, the `if err is not None` guard (line 1416) raises `ValueError` before the `hint_store.add_hints` call (line 1437). The coin records for blocks 0..K-1 are durably committed; their hints are not. No recovery path exists: on re-sync, `add_block` returns `ALREADY_HAVE_BLOCK` for those blocks, so `agg_state_change_summary` is never rebuilt for them.

### Impact Explanation
The hint table is the sole index used by `register_for_ph_updates` to resolve hinted coins for wallets. Permanent absence of hints for blocks 0..K-1 means any coin created with a `CREATE_COIN` hint in those blocks is invisible to wallets querying by hint — including CAT receives, NFT transfers, DID operations, and offer settlement outputs. This is permanent hint index corruption with direct security impact on wallet coin discovery.

### Likelihood Explanation
Reachable via the sync peer protocol. Any peer the node chooses to sync from can craft a batch (or simply serve one valid block followed by a tampered block). The attacker is banned after the fact, but the DB corruption is already durable. No special privileges are required beyond being a connectable peer.

### Recommendation
In `ingest_batch`, when `err is not None` but `state_change_summary is not None`, call `hint_store.add_hints` for the already-committed blocks before raising:

```python
state_change_summary, err = await self.add_prevalidated_blocks(...)
# Always persist hints for any blocks that were committed, even on error
if state_change_summary is not None:
    hints_to_add, _ = get_hints_and_subscription_coin_ids(
        state_change_summary,
        self.subscriptions.has_coin_subscription,
        self.subscriptions.has_puzzle_subscription,
    )
    await self.hint_store.add_hints(hints_to_add)
if err is not None:
    await peer.close(CONSENSUS_ERROR_BAN_SECONDS)
    raise ValueError(...)
```

### Proof of Concept
1. Stand up a local full node in sync mode.
2. Serve a batch of N valid blocks (with hinted `CREATE_COIN` outputs) followed by one block with a corrupted `pre_validation_result` (set `error = Err.INVALID_POSPACE.value`).
3. After the sync attempt fails and the peer is banned, query `hint_store.get_coin_ids(hint)` for hints from blocks 0..N-1.
4. Assert the result is empty — confirming the hints were never written despite the coin records being present in `coin_store`.

### Citations

**File:** chia/full_node/full_node.py (L1416-1437)
```python
            if err is not None:
                await peer.close(CONSENSUS_ERROR_BAN_SECONDS)
                raise ValueError(f"Failed to validate block batch {start_height} to {end_height}: {err}")
            if end_height - block_rate_height > 100:
                now = time.monotonic()
                block_rate = (end_height - block_rate_height) / (now - block_rate_time)
                block_rate_time = now
                block_rate_height = end_height

            self.log.info(
                f"Added blocks {start_height} to {end_height} ({block_rate:.3g} blocks/s) (from: {peer.peer_info.ip})"
            )
            peak: BlockRecord | None = self.blockchain.get_peak()
            if state_change_summary is not None:
                assert peak is not None
                # Hints must be added to the DB. The other post-processing tasks are not required when syncing
                hints_to_add, _ = get_hints_and_subscription_coin_ids(
                    state_change_summary,
                    self.subscriptions.has_coin_subscription,
                    self.subscriptions.has_puzzle_subscription,
                )
                await self.hint_store.add_hints(hints_to_add)
```

**File:** chia/full_node/full_node.py (L1686-1692)
```python
            if pre_validation_results[i].error is not None:
                self.log.error(
                    f"prevalidation failed for block {header_hash.hex()} height {block.height} "
                    f"from peer {peer_info}: {Err(pre_validation_results[i].error).name}"
                    f" {pre_validation_results[i].error_msg or ''}"
                )
                return agg_state_change_summary, Err(pre_validation_results[i].error)
```

**File:** chia/full_node/full_node.py (L1716-1745)
```python
            result, error, state_change_summary = await self.blockchain.add_block(
                block,
                pre_validation_results[i],
                vs.ssi,
                fork_info,
                prev_ses_block=vs.prev_ses_block,
                block_record=block_rec,
            )
            if error is None:
                blockchain.remove_extra_block(header_hash)

            if result == AddBlockResult.NEW_PEAK:
                # since this block just added a new peak, we've don't need any
                # fork history from fork_info anymore
                fork_info.reset(block.height, header_hash)
                assert state_change_summary is not None
                # Since all blocks are contiguous, we can simply append the rollback changes and npc results
                if agg_state_change_summary is None:
                    agg_state_change_summary = state_change_summary
                else:
                    # Keeps the old, original fork_height, since the next blocks will have fork height h-1
                    # Groups up all state changes into one
                    agg_state_change_summary = StateChangeSummary(
                        state_change_summary.peak,
                        agg_state_change_summary.fork_height,
                        agg_state_change_summary.rolled_back_records + state_change_summary.rolled_back_records,
                        agg_state_change_summary.removals + state_change_summary.removals,
                        agg_state_change_summary.additions + state_change_summary.additions,
                        agg_state_change_summary.new_rewards + state_change_summary.new_rewards,
                    )
```

**File:** chia/full_node/full_node.py (L1746-1749)
```python
            elif result in {AddBlockResult.INVALID_BLOCK, AddBlockResult.DISCONNECTED_BLOCK}:
                if error is not None:
                    self.log.error(f"Error: {error}, Invalid block from peer: {peer_info} ")
                return agg_state_change_summary, error
```

**File:** chia/full_node/full_node_api.py (L1851-1863)
```python
        hint_coin_ids = await self.full_node.hint_store.get_coin_ids_multi(
            cast(set[bytes], puzzle_hashes), max_items=max_items
        )

        hint_states: list[CoinState] = []
        if len(hint_coin_ids) > 0:
            hint_states = await self.full_node.coin_store.get_coin_states_by_ids(
                include_spent_coins=True,
                coin_ids=hint_coin_ids,
                min_height=request.min_height,
                max_items=len(hint_coin_ids),
            )
            states.update(hint_states)
```
