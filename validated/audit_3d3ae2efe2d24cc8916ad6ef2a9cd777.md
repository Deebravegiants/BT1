Based on the code inspection, this scenario does not constitute a real vulnerability.

`Bank::check_transactions_with_processed_slots` (runtime/src/bank/check_transactions.rs) performs two independent checks for every transaction: `check_age_and_compute_budget_limits` (which calls `check_transaction_age`) and then `check_status_cache`. [1](#0-0) 

`check_transaction_age` only validates that the `recent_blockhash` is within `max_age` of the current `blockhash_queue.last_hash_index` — the boundary case (`hash_index` difference `== max_age`) is explicitly and correctly treated as valid, which is intended, documented behavior (see the `test_is_hash_valid_for_age` / `test_get_hash_info_if_valid` tests) rather than a bug. [2](#0-1) [3](#0-2) 

The actual replay-prevention mechanism is the status cache check, which is separate from blockhash age and does not depend on root promotion. `check_status_cache` looks up `sanitized_tx.message_hash()` keyed by `recent_blockhash` using `self.ancestors` — the *bank's own ancestor set*, not the set of rooted slots: [4](#0-3) 

`StatusCache::get_status` matches an entry if its recorded slot is contained in `ancestors` **or** is a root: [5](#0-4) 

Since a child bank at slot `N+1` derived from bank `N` (same fork) always has `N` in its `ancestors` set (populated when the bank is forked from its parent), a transaction processed and inserted into the status cache at slot `N` will be found as `AlreadyProcessed` when resubmitted to any descendant bank at `N+1`, *regardless of whether the status-cache root has advanced past `N`*. Root promotion is only relevant for pruning of purged/non-descendant forks and long-term retention (`add_root`/`purge_roots`), not for basic parent→child duplicate detection. The attacker's premise — that resubmission "before status-cache root advances past N" evades detection — is incorrect because the ancestors-based lookup does not require rooting at all.

This exactly matches the existing regression test `test_update_transaction_statuses` in `ledger/src/blockstore_processor.rs`, which explicitly asserts a second identical submission returns `Err(TransactionError::AlreadyProcessed)`: [6](#0-5) 

#No vulnerability found for this question.

### Citations

**File:** runtime/src/bank/check_transactions.rs (L103-127)
```rust
    pub fn check_transactions_with_processed_slots<Tx: TransactionWithMeta>(
        &self,
        sanitized_txs: &[impl core::borrow::Borrow<Tx>],
        lock_results: &[TransactionResult<()>],
        max_age: usize,
        collect_processed_slots: bool,
        strict_nonce_size_check: bool,
        error_counters: &mut TransactionErrorMetrics,
    ) -> (Vec<TransactionCheckResult>, Option<Vec<Option<Slot>>>) {
        let lock_results = self.filter_v1_transactions(sanitized_txs, lock_results);

        let lock_results = self.check_age_and_compute_budget_limits(
            sanitized_txs,
            lock_results,
            max_age,
            strict_nonce_size_check,
            error_counters,
        );
        self.check_status_cache(
            sanitized_txs,
            lock_results,
            collect_processed_slots,
            error_counters,
        )
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

**File:** runtime/src/bank/check_transactions.rs (L337-347)
```rust
    fn get_processed_slot(
        &self,
        sanitized_tx: &impl TransactionWithMeta,
        status_cache: &BankStatusCache,
    ) -> Option<Slot> {
        let key = sanitized_tx.message_hash();
        let transaction_blockhash = sanitized_tx.recent_blockhash();
        status_cache
            .get_status(key, transaction_blockhash, &self.ancestors)
            .map(|status| status.0)
    }
```

**File:** accounts-db/src/blockhash_queue.rs (L130-132)
```rust
    fn is_hash_index_valid(last_hash_index: u64, max_age: usize, hash_index: u64) -> bool {
        last_hash_index - hash_index <= max_age as u64
    }
```

**File:** runtime/src/status_cache.rs (L142-166)
```rust
    /// Check if the key is in any of the forks in the ancestors set and
    /// with a certain blockhash.
    pub fn get_status<K: AsRef<[u8]>>(
        &self,
        key: K,
        transaction_blockhash: &Hash,
        ancestors: &Ancestors,
    ) -> Option<(Slot, T)> {
        let map = self.cache.get(transaction_blockhash)?;
        let (_, index, keymap) = map;
        let max_key_index = key.as_ref().len().saturating_sub(CACHED_KEY_SIZE + 1);
        let index = (*index).min(max_key_index);
        let key_slice: &[u8; CACHED_KEY_SIZE] =
            arrayref::array_ref![key.as_ref(), index, CACHED_KEY_SIZE];
        if let Some(stored_forks) = keymap.get(key_slice) {
            let res = stored_forks
                .iter()
                .find(|(f, _)| ancestors.contains_key(f) || self.roots.contains(f))
                .cloned();
            if res.is_some() {
                return res;
            }
        }
        None
    }
```

**File:** ledger/src/blockstore_processor.rs (L4051-4054)
```rust
        assert_eq!(
            bank.transfer(10_001, &mint_keypair, &pubkey),
            Err(TransactionError::AlreadyProcessed)
        );
```
