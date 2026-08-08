This is analyzed on the same bank/blockhash-queue instance, so it confirms the hypothesis in the question is mathematically impossible.

`is_hash_index_valid(last_hash_index, max_age, hash_index)` checks `last_hash_index - hash_index <= max_age` [1](#0-0) . A smaller `max_age` is strictly more restrictive (fewer hash indices satisfy the inequality) than a larger `max_age`, given the same queue state (same `last_hash_index`). Since `check_transactions_with_forwarding_delay` computes `max_age = max_processing_age().saturating_sub(MAX_TRANSACTION_FORWARDING_DELAY).saturating_sub(forward_offset)` [2](#0-1) , this value is always `<= max_processing_age()`, the plain value used by `check_transaction_without_status_cache` [3](#0-2) .

Both paths funnel into `check_transaction_age`, which for non-nonce hashes checks `hash_queue.get_hash_info_if_valid(recent_blockhash, max_age)` [4](#0-3) . If the plain-hash check passes with the smaller (forwarding-delay-adjusted) `max_age`, it is mathematically guaranteed to also pass with the larger, plain `max_processing_age()` — the "forwarding-delay-adjusted window" is a strict subset of the "leader window" on the same queue state, never the reverse. So the premise of the question — a blockhash valid under the forwarder's reduced max_age but stale under the leader's plain max_age — cannot occur; it's backwards from how the code actually behaves.

For the nonce-advanceability branch (`check_nonce_transaction_validity`), the verdict depends only on whether `recent_blockhash != next_durable_nonce.as_hash()` plus the on-chain nonce account state [5](#0-4)  — it does not depend on `max_age` at all. `max_age` only gates the plain-blockhash branch checked *before* falling through to the nonce branch. So the two `max_age` values cannot cause divergent nonce-advanceability verdicts either: for a given tx and a given bank/queue state, nonce-advanceability is independent of which `max_age` variant is used.

Across sequential leaders (different banks/slots), the durable-nonce single-execution property is enforced independently: nonce advancement requires the transaction's `recent_blockhash` to equal that nonce account's currently stored durable-nonce value, and each successful advance rotates the on-chain nonce hash forward via `AdvanceNonceAccount`, invalidating the original nonce value for replay/reuse in a subsequent block. This is a separate mechanism from the blockhash-queue-age check discussed here, and the question's proof idea (comparing verdicts within one bank instance) does not establish any double-processing since the status-cache and on-chain nonce state (not `max_age`) are what prevent the "second commit."

No vulnerability found for this question.

### Citations

**File:** accounts-db/src/blockhash_queue.rs (L130-132)
```rust
    fn is_hash_index_valid(last_hash_index: u64, max_age: usize, hash_index: u64) -> bool {
        last_hash_index - hash_index <= max_age as u64
    }
```

**File:** runtime/src/bank/check_transactions.rs (L40-50)
```rust
        let max_tx_fwd_delay = MAX_TRANSACTION_FORWARDING_DELAY;

        self.check_transactions(
            transactions,
            filter,
            self.max_processing_age()
                .saturating_sub(max_tx_fwd_delay)
                .saturating_sub(forward_transactions_to_leader_at_slot_offset as usize),
            false,
            &mut error_counters,
        )
```

**File:** runtime/src/bank/check_transactions.rs (L75-101)
```rust
    pub fn check_transaction_without_status_cache(
        &self,
        tx: &impl SVMMessage,
        max_age: usize,
        error_counters: &mut TransactionErrorMetrics,
    ) -> TransactionResult<Option<Pubkey>> {
        let feature_set: &FeatureSet = &self.feature_set;
        let feature_snapshot = feature_set.snapshot();
        let enable_tx_v1 = feature_snapshot.enable_tx_v1;

        if !enable_tx_v1 && tx.version() == TransactionVersion::Number(1) {
            return Err(TransactionError::UnsupportedVersion);
        }

        let hash_queue = self.blockhash_queue.read().unwrap();
        let next_durable_nonce = hash_queue.next_durable_nonce();

        self.check_transaction_age(
            tx,
            max_age,
            &next_durable_nonce,
            &hash_queue,
            error_counters,
            true, // strict_nonce_size_check
            true, // strict_nonce_authority_check
        )
    }
```

**File:** runtime/src/bank/check_transactions.rs (L239-256)
```rust
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

**File:** runtime/src/bank/check_transactions.rs (L258-284)
```rust
    pub(super) fn check_nonce_transaction_validity(
        &self,
        message: &impl SVMMessage,
        next_durable_nonce: &DurableNonce,
        strict_nonce_size_check: bool,
        strict_nonce_authority_check: bool,
    ) -> Option<(Pubkey, u64)> {
        let nonce_is_advanceable = message.recent_blockhash() != next_durable_nonce.as_hash();
        if !nonce_is_advanceable {
            return None;
        }

        let (nonce_address, nonce_data) =
            self.load_message_nonce_data(message, strict_nonce_size_check)?;

        if strict_nonce_authority_check
            && !message
                .get_ix_signers(NONCED_TX_MARKER_IX_INDEX as usize)
                .any(|signer| signer == &nonce_data.authority)
        {
            return None;
        }

        let previous_lamports_per_signature = nonce_data.get_lamports_per_signature();

        Some((nonce_address, previous_lamports_per_signature))
    }
```
