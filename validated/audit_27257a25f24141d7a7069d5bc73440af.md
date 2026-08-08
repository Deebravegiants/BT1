Based on my analysis of the account lock validation paths, this claimed bypass does not hold up against the actual code.

Key facts:
1. `has_duplicates()` in `accounts-db/src/account_locks.rs` operates on the full `AccountKeys` type, which is constructed from `AccountKeys::new(static_keys, Some(dynamic_keys))` and iterates across **both** static and dynamic (ALT-resolved writable/readonly) keys together via a single iterator. The existing unit tests `test_validate_account_locks_duplicate_dynamic` explicitly prove that a duplicate spanning a static key and an ALT-resolved readonly key is caught and rejected with `TransactionError::AccountLoadedTwice`. [1](#0-0) 

2. Every code path that constructs a lockable transaction resolves ALT lookups **before** calling `validate_account_locks`, not after: in `translate_to_runtime_view`, `load_addresses_for_view` (which performs the ALT resolution) is called first, then `RuntimeTransaction::<ResolvedTransactionView<_>>::try_new` builds the full merged key set, and only then is `validate_account_locks(view.account_keys(), ...)` invoked over that merged set. [2](#0-1) 

3. `RuntimeTransaction::try_create` (used by RPC, replay, and other paths) resolves addresses via `SanitizedTransaction::try_new(..., address_loader, ...)` synchronously as part of message construction, before the resulting `SanitizedTransaction`'s `account_keys()` is ever handed to a lock-taking function like `Accounts::lock_accounts` or `Bank::prepare_sanitized_batch_with_results`. [3](#0-2) 

4. Regarding the specific mechanism cited in the question — `Bank::resanitize_transaction_minimally`'s use of `load_addresses_from_ref` — this function discards the newly-resolved addresses (bound to `_addresses`) and uses the call **solely to detect ALT resolution failure** (e.g., an ALT closed/expired since initial resolution). It does not feed the freshly-resolved addresses back into the transaction's account key set used for locking; the transaction retains its already-resolved (and already `validate_account_locks`-checked) `account_keys()` from its original construction. [4](#0-3) 

Since the newly-resolved (potentially different) addresses from `resanitize_transaction_minimally` are never used to construct the lock set — `AccountLocks::can_lock_accounts`/`lock_accounts` in `accounts-db/src/account_locks.rs` always operate on the transaction's already-validated `account_keys()` — there is no path by which a duplicate introduced only in a "re-resolution" is ever locked without going through `has_duplicates()`. All batch and unified-scheduler lock paths (`Accounts::lock_accounts`, `Bank::prepare_sanitized_batch_with_results`, `validate_entry_transactions`, `do_create_task`) consume the already-resolved, already-checked `AccountKeys`. [5](#0-4) [6](#0-5) 

#No vulnerability found for this question.

### Citations

**File:** accounts-db/src/account_locks.rs (L241-254)
```rust
    #[test]
    fn test_validate_account_locks_duplicate_dynamic() {
        let duplicate_key = Pubkey::new_unique();
        let static_keys = &[duplicate_key];
        let dynamic_keys = LoadedAddresses {
            writable: vec![Pubkey::new_unique()],
            readonly: vec![duplicate_key],
        };
        let account_keys = AccountKeys::new(static_keys, Some(&dynamic_keys));
        assert_eq!(
            validate_account_locks(account_keys, MAX_TX_ACCOUNT_LOCKS),
            Err(TransactionError::AccountLoadedTwice)
        );
    }
```

**File:** core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs (L439-452)
```rust
    let (loaded_addresses, deactivation_slot) = load_addresses_for_view(&view, bank)?;

    let Ok(view) = RuntimeTransaction::<ResolvedTransactionView<_>>::try_new(
        view,
        loaded_addresses,
        bank.get_reserved_account_keys(),
    ) else {
        return Err(PacketHandlingError::Sanitization);
    };

    // Validate no duplicate accounts (must be after resolution to catch ALT duplicates)
    if validate_account_locks(view.account_keys(), transaction_account_lock_limit).is_err() {
        return Err(PacketHandlingError::LockValidation);
    }
```

**File:** runtime-transaction/src/runtime_transaction/sdk_transactions.rs (L113-134)
```rust
    pub fn try_from(
        statically_loaded_runtime_tx: RuntimeTransaction<SanitizedVersionedTransaction>,
        address_loader: impl AddressLoader,
        reserved_account_keys: &HashSet<Pubkey>,
    ) -> Result<Self> {
        let hash = *statically_loaded_runtime_tx.message_hash();
        let is_simple_vote_tx = statically_loaded_runtime_tx.is_simple_vote_transaction();
        let sanitized_transaction = SanitizedTransaction::try_new(
            statically_loaded_runtime_tx.transaction,
            hash,
            is_simple_vote_tx,
            address_loader,
            reserved_account_keys,
        )?;

        let tx = Self {
            transaction: sanitized_transaction,
            meta: statically_loaded_runtime_tx.meta,
        };

        Ok(tx)
    }
```

**File:** runtime/src/bank.rs (L3794-3806)
```rust
        if self.slot() > alt_invalidation_slot {
            // The address table lookup **may** have expired, but the
            // expiration is not guaranteed since there may have been
            // skipped slot.
            // If the addresses still resolve here, then the transaction is still
            // valid, and we can continue with processing.
            // If they do not, then the ATL has expired and the transaction
            // can be dropped.
            let (_addresses, _deactivation_slot) =
                self.load_addresses_from_ref(transaction.message_address_table_lookups())?;
        }

        Ok(())
```

**File:** accounts-db/src/accounts.rs (L461-470)
```rust
        // Validate the account locks, then get keys and is_writable if successful validation.
        // We collect to fully evaluate before taking the account_locks mutex.
        let validated_batch_keys = txs
            .zip(results)
            .map(|(tx, result)| {
                result
                    .and_then(|_| validate_account_locks(tx.account_keys(), tx_account_lock_limit))
                    .map(|_| TransactionAccountLocksIterator::new(tx).accounts_with_is_writable())
            })
            .collect::<Vec<_>>();
```

**File:** unified-scheduler-logic/src/lib.rs (L1332-1358)
```rust
        // It's crucial for tasks to be validated with
        // `account_locks::validate_account_locks()` prior to the creation.
        // That's because it's part of protocol consensus regarding the
        // rejection of blocks containing malformed transactions
        // (`AccountLoadedTwice` and `TooManyAccountLocks`). Even more,
        // `SchedulingStateMachine` can't properly handle transactions with
        // duplicate addresses (those falling under `AccountLoadedTwice`).
        //
        // However, it's okay for now not to call `::validate_account_locks()`
        // here.
        //
        // Currently `replay_stage` is always calling
        //`::validate_account_locks()` regardless of whether unified-scheduler
        // is enabled or not at the blockstore
        // (`Bank::prepare_sanitized_batch()` is called in
        // `process_entries()`).
        //
        // As for `banking_stage` with unified scheduler, it will need to run
        // `validate_account_locks()` at least once somewhere in the code path.
        // In the distant future, this function (`create_task()`) should be
        // adjusted so that both stages do the checks before calling this or do
        // the checks here, to simplify the two code paths regarding the
        // essential `validate_account_locks` validation.
        //
        // Lastly, `validate_account_locks()` is currently called in
        // `DefaultTransactionHandler::handle()` via
        // `Bank::prepare_unlocked_batch_from_single_tx()` as well.
```
