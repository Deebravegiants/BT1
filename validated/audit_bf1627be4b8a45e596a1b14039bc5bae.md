This gives a clear answer. `enqueue_on_chain_accounts_lt_hash_updates` explicitly deduplicates by iterating in reverse and keeping only the newest version per pubkey (the lt-hash, which is the consensus-critical hash), while `update_bank_hash_stats` iterates over every entry, including duplicates, without deduplication.

### Title
No exploitable bank-hash divergence from duplicate-key writes in `commit_transactions` - ([File: runtime/src/bank.rs])

### Summary
Post-SIMD-83, two writable-conflicting transactions can validly co-exist in the same batch/entry, as confirmed by `test_accounts_locks_intrabatch_conflicts` in `accounts-db/src/accounts.rs`. `collect_accounts_to_store` in `runtime/src/account_saver.rs` does append one entry per transaction touching a pubkey (no dedup), and `update_bank_hash_stats` in `runtime/src/bank.rs` naively iterates and accumulates stats for every entry, including stale duplicates, while `enqueue_on_chain_accounts_lt_hash_updates` in `runtime/src/bank/accounts_lt_hash.rs` correctly deduplicates keeping only the last write. However this inconsistency is fully deterministic and identical on every honest validator, since it depends only on the fixed transaction order within the entry/block, not on any node-local or accounts-db-implementation-specific behavior.

### Finding Description
`collect_accounts_to_store` ( [1](#0-0) ) iterates `processing_results.iter().zip(txs)` in strict transaction order and appends one `(pubkey, account)` tuple per touched account per transaction, without deduplicating repeated pubkeys across transactions in the same batch. `commit_transactions` then feeds this vector to two consumers:

- `update_bank_hash_stats` ( [2](#0-1)  ) iterates `0..accounts.len()` and calls `stats.update(&account)` for *every* entry, so if the same pubkey appears twice (once per conflicting transaction), both the stale and final versions are folded into `BankHashStats` (`num_updated_accounts`, `total_data_len`, `num_lamports_stored`, etc.).
- `enqueue_on_chain_accounts_lt_hash_updates` ( [3](#0-2) ) explicitly processes accounts in reverse order and skips a pubkey once already seen (`if !seen_accounts.insert(*address) { continue; }`), so only the *last* write per pubkey mixes into the consensus-critical accounts lt-hash.

This means `BankHashStats` (a diagnostic/snapshot-serialized struct) can double count duplicate writes within the same block, while the actual accounts lt-hash used for `bank.hash()` correctly reflects only the final write. Critically, both code paths are pure functions of the *same* deterministic input — the transaction order fixed by the block/entry — so every honest validator replaying the identical block executes identical code with identical inputs and produces identical (internally-inconsistent-but-consistent) `BankHashStats` and identical lt-hash. There is no "accounts-db implementation that dedups differently" reachable by an unprivileged attacker within this single codebase; that scenario is hypothetical/speculative about alternate client implementations, not a demonstrable divergence within Agave itself.

### Impact Explanation
No qualifying impact under scope: this does not cause bank-hash divergence between honest Agave nodes, value loss/creation, double settlement, or a security-relevant undeclared mutation. `BankHashStats` accumulation is not itself part of the accounts lt-hash mixed into `bank.hash()` (that is handled correctly and separately, deduplicated, by `enqueue_on_chain_accounts_lt_hash_updates`). Even if `BankHashStats`' internal counters are "wrong" relative to a naive last-write-wins expectation, they are wrong identically and deterministically on every node, so no fork or safety violation results.

### Likelihood Explanation
Not applicable — the described precondition (intra-batch conflicting writes to the same account) is real and permitted since SIMD-83 ( [4](#0-3) , [5](#0-4) ), but the claimed consequence (cross-node bank-hash divergence from ordering disagreement) does not follow, because the actual consensus hash path already deduplicates correctly and consistently.

### Recommendation
No security fix required. If desired for correctness/observability of `BankHashStats` (a non-consensus diagnostic structure), `update_bank_hash_stats` could be updated to dedupe by pubkey (keep last) before accumulating, mirroring the approach already used in `enqueue_on_chain_accounts_lt_hash_updates`, purely to make the reported statistics semantically match "final state per block" rather than "per write."

### Proof of Concept
Not applicable as a security PoC; this is not an exploitable divergence. A correctness-only test could assert that `BankHashStats.num_updated_accounts` for a block with two same-slot transactions writing the same account counts 2 writes instead of 1, to document the (non-security) discrepancy between `BankHashStats` and the deduplicated lt-hash behavior, but this would not demonstrate any consensus break, fund loss, or bounty-qualifying impact.

### Citations

**File:** runtime/src/account_saver.rs (L67-72)
```rust
    for (index, (processing_result, transaction)) in processing_results.iter().zip(txs).enumerate()
    {
        let Some(processed_tx) = processing_result.processed_transaction() else {
            // Don't store any accounts if tx wasn't executed
            continue;
        };
```

**File:** runtime/src/bank.rs (L4307-4315)
```rust
    fn update_bank_hash_stats<'a>(&self, accounts: &impl StorableAccounts<'a>) {
        let mut stats = BankHashStats::default();
        (0..accounts.len()).for_each(|i| {
            accounts.account(i, |account| {
                stats.update(&account);
            })
        });
        self.bank_hash_stats.accumulate(&stats);
    }
```

**File:** runtime/src/bank/accounts_lt_hash.rs (L46-79)
```rust
        let seen_accounts_freelist = seen_accounts_freelist();
        let mut seen_accounts = seen_accounts_freelist.try_pop().unwrap_or_default();
        let async_progress = &self.accounts_lt_hash_async_progress;
        let thread_pool = accounts_hasher_thread_pool();

        // process accounts in reverse because we must only count the latest version of each account
        for index in (0..accounts.len()).rev() {
            let address = accounts.pubkey(index);
            if !seen_accounts.insert(*address) {
                // we've already enqueued a newer update for the same account; skip this one
                continue;
            }
            let prev_account = self
                .rc
                .accounts
                .load_with_fixed_root_do_not_populate_read_cache(&self.ancestors, address)
                .map(|(account, _slot)| account);
            let curr_account = accounts.account(index, |account| {
                (account.lamports() != 0).then(|| account.take_account())
            });
            if prev_account.is_none() && curr_account.is_none() {
                // the account was ephemeral; skip it
            } else {
                // the account was modified; enqueue this update
                async_progress.spawn(
                    thread_pool,
                    AccountsLtHashUpdate {
                        address: *address,
                        prev_account,
                        curr_account,
                    },
                );
            }
        }
```

**File:** accounts-db/src/accounts.rs (L1277-1295)
```rust
        // wr conflict in-batch succeeds
        let accounts = Accounts::new(accounts_db.clone());
        let results = accounts.lock_accounts(
            [w_tx.clone(), r_tx.clone()].iter(),
            [Ok(()), Ok(())].into_iter(),
            MAX_TX_ACCOUNT_LOCKS,
        );

        assert_eq!(results, vec![Ok(()), Ok(())]);

        // ww conflict in-batch succeeds
        let accounts = Accounts::new(accounts_db);
        let results = accounts.lock_accounts(
            [w_tx, r_tx].iter(),
            [Ok(()), Ok(())].into_iter(),
            MAX_TX_ACCOUNT_LOCKS,
        );

        assert_eq!(results, vec![Ok(()), Ok(())]);
```

**File:** ledger/src/blockstore_processor.rs (L253-268)
```rust
/// Validate an entry's transactions before scheduling: each transaction's account
/// locks (count and duplicates), and rejection of duplicate message hashes within
/// the entry. Does not take account locks - the unified scheduler orders conflicts.
/// Post-SIMD-83 the duplicate-message-hash check is what rejects an entry that
/// replays the same transaction twice (it no longer conflicts on locks).
fn validate_entry_transactions(
    transactions: &[RuntimeTransaction<SanitizedTransaction>],
    tx_account_lock_limit: usize,
) -> Result<()> {
    let mut batch_message_hashes = AHashSet::with_capacity(transactions.len());

    for transaction in transactions {
        validate_account_locks(transaction.account_keys(), tx_account_lock_limit)?;
        if !batch_message_hashes.insert(transaction.message_hash()) {
            return Err(TransactionError::AlreadyProcessed);
        }
```
