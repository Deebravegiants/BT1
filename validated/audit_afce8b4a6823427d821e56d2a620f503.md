### Title
Status-cache root pruning can evict a committed transaction's dedup entry one slot before its blockhash ages out of the BlockhashQueue, enabling exact-blockhash transaction replay - ([File: runtime/src/status_cache.rs] / [File: accounts-db/src/blockhash_queue.rs])

### Summary
`StatusCache::purge_roots` (`runtime/src/status_cache.rs`) prunes down to exactly `max_root_entries` (== `MAX_RECENT_BLOCKHASHES`) roots, while `BlockhashQueue::purge` (`accounts-db/src/blockhash_queue.rs`) keeps `max_age + 1` valid hash entries due to a documented off-by-one in its age comparison (`<=` instead of `<`). This mismatch creates a deterministic one-slot window in which a previously committed transaction's blockhash is still `is_hash_valid_for_age` in `check_transaction_age`, but its status-cache entry (used for `AlreadyProcessed`/dedup detection) has already been purged by `purge_roots`.

### Finding Description
- `MAX_ROOT_ENTRIES` is defined as `MAX_RECENT_BLOCKHASHES` [1](#0-0) .
- `purge_roots` computes `num_roots_to_purge = roots.len() - max_root_entries` and uses `select_nth_unstable` to find a cutoff such that exactly `max_root_entries` roots survive (`root > cutoff`), and correspondingly evicts `cache` and `slot_deltas` entries with `fork <= cutoff` [2](#0-1) . This means a transaction committed at slot `S` has its status-cache entry evicted exactly when the `(max_root_entries+1)`-th newer root is added (i.e., once root `S + max_root_entries` becomes a root).
- `BlockhashQueue::purge` retains any hash whose `last_hash_index - hash_index <= max_age` [3](#0-2) . Because of the `<=`, the queue holds `max_age + 1` valid entries rather than `max_age` — this exact off-by-one is called out in the queue's own test: "the queue actually holds one more entry than the max age... this is likely the result of an unintentional off-by-one error in the past" [4](#0-3) .
- `check_transaction_age` (the sole gate for blockhash freshness on resubmission) only consults `hash_queue.get_hash_info_if_valid(recent_blockhash, max_age)`; it does not itself re-check the status cache [5](#0-4) . The blockhash for slot `S` therefore remains "valid for age" through the root at `S + max_age` (age == max_age, `<=` passes), while the status-cache entry for slot `S` is already gone as soon as root `S + max_root_entries` (== `S + max_age`, since both constants equal `MAX_RECENT_BLOCKHASHES`) is added — i.e., at the very same root height where the boundary case in the blockhash queue is still valid.
- The net effect: at the root exactly `MAX_RECENT_BLOCKHASHES` slots after slot `S`, the status-cache dedup entry for a signature committed in `S` has been purged (`get_status` returns `None`), but the transaction's `recent_blockhash` is still accepted by `check_transaction_age`. Resubmitting the identical signed transaction at that root height passes both the blockhash-age check and the status-cache dedup check, and would be processed/committed a second time.

### Impact Explanation
This is a double-settlement / transaction-replay bug: an identical, already-executed and already-fee-charged transaction (e.g., a transfer, a program invocation with side effects) can be re-applied to on-chain state within a narrow, deterministic window, causing value duplication or repeated state mutation that should have "settled exactly once." This falls under the double-apply / value-duplication category described in the prompt (replay outrunning blockhash aging), scoped to `runtime/src/status_cache.rs` and `accounts-db/src/blockhash_queue.rs`.

### Likelihood Explanation
The trigger condition is a fixed, predictable root-height offset (`MAX_RECENT_BLOCKHASHES` slots after the original commit slot, ~2 minutes at current cluster timing), not a special attacker capability — the attacker only needs to (a) keep the original signed transaction bytes, and (b) resubmit it via a public RPC/TPU endpoint at the correct slot/root height, which they can observe via ordinary `getSlot`/`getBlockHeight` polling. No leader, validator, or gossip control is required — only precise timing of a normal client resubmission, which matches the stated "unprivileged attacker who controls transaction timing" threat model. The window is narrow (on the order of a single root advance), so it requires accurate timing but is fully within reach of an automated bot.

### Recommendation
Bring the two aging windows into strict lockstep: either (1) fix the `BlockhashQueue` off-by-one by changing `is_hash_index_valid` to a strict `<` comparison (or reduce its effective retained window by one), or (2) change `StatusCache::purge_roots` to retain `max_root_entries + 1` roots to match the blockhash queue's actual valid window, and add a debug_assert/invariant test asserting that any blockhash still `is_hash_valid_for_age` always has a corresponding retained status-cache root for the slot it was registered in.

### Proof of Concept
Rust integration test sketch (bank-level):
```rust
#[test]
fn test_status_cache_purge_outruns_blockhash_age() {
    // 1. Create bank, submit tx at slot S with blockhash H, commit (bank.process_transaction).
    // 2. Advance MAX_RECENT_BLOCKHASHES roots (new_from_parent + set_root each slot),
    //    keeping track of the exact slot where purge_roots evicts slot S from status_cache.roots().
    // 3. At that root height, assert:
    assert!(bank.is_blockhash_valid(&H)); // still valid per check_transaction_age
    assert_eq!(
        bank.status_cache.read().unwrap().get_status(sig, &H, &ancestors),
        None // dedup entry already purged
    );
    // 4. Resubmit the identical signed transaction using blockhash H:
    let result = bank.process_transaction(&identical_tx);
    // Expected (documenting the bug): Ok(()) instead of Err(TransactionError::AlreadyProcessed) / duplicate application of state changes.
    assert_ne!(result, Err(TransactionError::AlreadyProcessed));
}
```
This mirrors the existing `test_root_expires` / `test_max_root_entries` tests in `runtime/src/status_cache.rs` and the `test_len`/`test_change_max_age` tests in `accounts-db/src/blockhash_queue.rs`, combined at the `Bank` level to demonstrate that the two purge horizons are not equal, invalidating the "settles exactly once" invariant for the boundary blockhash age.

### Citations

**File:** runtime/src/status_cache.rs (L18-21)
```rust
// The maximum number of entries to store in the cache. This is the same as the number of recent
// blockhashes because we automatically reject txs that use older blockhashes so we don't need to
// track those explicitly.
const MAX_ROOT_ENTRIES: usize = MAX_RECENT_BLOCKHASHES;
```

**File:** runtime/src/status_cache.rs (L241-257)
```rust
    pub fn purge_roots(&mut self) {
        let max_root_entries = self.max_root_entries();
        if self.roots.len() > max_root_entries {
            let num_roots_to_purge = self.roots.len() - max_root_entries;
            let mut roots = self
                .roots
                .iter()
                .copied()
                .collect::<SmallVec<[Slot; 0x200]>>();
            let (_, cutoff, _) = roots.select_nth_unstable(num_roots_to_purge - 1);
            let cutoff = *cutoff;

            self.roots.retain(|root| *root > cutoff);
            self.cache.retain(|_, (fork, _, _)| *fork > cutoff);
            self.slot_deltas.retain(|slot, _| *slot > cutoff);
        }
    }
```

**File:** accounts-db/src/blockhash_queue.rs (L130-156)
```rust
    fn is_hash_index_valid(last_hash_index: u64, max_age: usize, hash_index: u64) -> bool {
        last_hash_index - hash_index <= max_age as u64
    }

    pub fn register_hash(&mut self, hash: &Hash, lamports_per_signature: u64) {
        self.last_hash_index += 1;
        self.purge();
        self.hashes.insert(
            *hash,
            HashInfo {
                fee_calculator: FeeCalculator::new(lamports_per_signature),
                hash_index: self.last_hash_index,
                timestamp: timestamp(),
            },
        );

        self.last_hash = Some(*hash);
        self.refresh_durable_nonce();
    }

    fn purge(&mut self) {
        if self.hashes.len() >= self.max_age {
            self.hashes.retain(|_, info| {
                Self::is_hash_index_valid(self.last_hash_index, self.max_age, info.hash_index)
            });
        }
    }
```

**File:** accounts-db/src/blockhash_queue.rs (L273-293)
```rust
    #[test]
    fn test_len() {
        const MAX_AGE: usize = 10;
        let mut hash_queue = BlockhashQueue::new(MAX_AGE);
        assert_eq!(hash_queue.hashes.len(), 0);

        for _ in 0..MAX_AGE {
            hash_queue.register_hash(&Hash::new_unique(), 0);
        }
        assert_eq!(hash_queue.hashes.len(), MAX_AGE);

        // Show that the queue actually holds one more entry than the max age.
        // This is because the most recent hash is considered to have an age of 0,
        // which is likely the result of an unintentional off-by-one error in the past.
        hash_queue.register_hash(&Hash::new_unique(), 0);
        assert_eq!(hash_queue.hashes.len(), MAX_AGE + 1);

        // Ensure that no additional entries beyond `MAX_AGE + 1` are added
        hash_queue.register_hash(&Hash::new_unique(), 0);
        assert_eq!(hash_queue.hashes.len(), MAX_AGE + 1);
    }
```

**File:** runtime/src/bank/check_transactions.rs (L229-256)
```rust
    fn check_transaction_age(
        &self,
        tx: &impl SVMMessage,
        max_age: usize,
        next_durable_nonce: &DurableNonce,
        hash_queue: &BlockhashQueue,
        error_counters: &mut TransactionErrorMetrics,
        strict_nonce_size_check: bool,
        strict_nonce_authority_check: bool,
    ) -> TransactionResult<Option<Pubkey>> {
        let recent_blockhash = tx.recent_blockhash();
        if hash_queue
            .get_hash_info_if_valid(recent_blockhash, max_age)
            .is_some()
        {
            Ok(None)
        } else if let Some((nonce_address, _)) = self.check_nonce_transaction_validity(
            tx,
            next_durable_nonce,
            strict_nonce_size_check,
            strict_nonce_authority_check,
        ) {
            Ok(Some(nonce_address))
        } else {
            error_counters.blockhash_not_found += 1;
            Err(TransactionError::BlockhashNotFound)
        }
    }
```
