### Title
Deleting an account with a pending `PromiseYield` leaves orphaned yield state (`PromiseYieldReceipt`/`PromiseYieldStatus`/yield-id mappings) that is never storage-accounted or cleaned up - (File: `runtime/runtime/src/actions.rs`, `core/store/src/utils/mod.rs`)

### Summary
`action_delete_account` removes an account's `Account`, `ContractCode`, access keys/gas-key nonces, and `ContractData` via `remove_account`, but it never checks for, nor cleans up, any pending `PromiseYield` state for that account: `TrieKey::PromiseYieldReceipt`, `TrieKey::PromiseYieldStatus`, `TrieKey::YieldIdToDataId`/`DataIdToYieldId`, or the corresponding entry still sitting in the global `PromiseYieldTimeout` queue. This is the same bug class as the C4 finding: an object ("NFT") is destroyed while a dependent reference ("delegation") to it survives, causing bloat, wasted work, and (here) unaccounted/free storage.

### Finding Description
`remove_account` in [1](#0-0)  only removes the `Account`, `ContractCode`, access keys and gas-key nonces, and contract-data entries for the account. It does not touch `PromiseYieldReceipt`, `PromiseYieldStatus`, or the yield-id mapping columns, even though these are listed as account-scoped columns in `TrieKey::COLUMNS_WITH_ACCOUNT_ID_IN_KEY` ( [2](#0-1) ), and are keyed by `(receiver_id, data_id)` exactly like `ContractData` ( [3](#0-2) , `:435`).

`action_delete_account` ( [4](#0-3) ) checks account storage-usage size and gas-key balances, but performs no check for an in-flight `PromiseYield` on the account before allowing deletion, and `validate_delete_action` ( [5](#0-4) ) only validates the `beneficiary_id`.

A contract can call `promise_yield_create`, which stores `PromiseYieldStatus::Yielded` and (if it's the actor's own function-call result) a `PromiseYieldReceipt` keyed to the account, plus enqueues a `PromiseYieldTimeout` entry ( [6](#0-5) , `runtime/runtime/src/ext.rs:353-369`). The same account (or a receipt whose final action is `DeleteAccount`) can then delete itself; `remove_account` deletes the `Account` record but the `PromiseYieldReceipt`/`PromiseYieldStatus`/yield-id-mapping trie entries for that account_id remain, and the shard-global `PromiseYieldTimeout` entry pointing at it also survives (it is never per-account-swept — `enqueue_promise_yield_timeout` in [7](#0-6) ).

When the timeout later fires, `resolve_promise_yield_timeouts` ( [8](#0-7) ) finds the stale `PromiseYieldReceipt` still present via `contains_key`, and unconditionally synthesizes and forwards a `PromiseResume` receipt to the now-deleted account. On processing, `process_receipt`'s `PromiseResume` branch ( [9](#0-8) ) finds the surviving `PromiseYieldReceipt`, removes it, clears `PromiseYieldStatus`/yield-id mappings, and — critically — calls `set_received_data` to write a new `ReceivedData` trie entry keyed to the deleted `account_id` ( [10](#0-9) ), then invokes `apply_action_receipt` for the parked yield receipt against that account. Inside `apply_action_receipt` ( [11](#0-10) ) the runtime looks up `get_account`, finds `None`, and `check_account_existence` ( [12](#0-11) ) rejects most actions with `AccountDoesNotExist`, but only *after* the `ReceivedData` write, the yield-receipt removal, and the fee/compute accounting for this whole receipt chain have already occurred against an account with no storage-staking backing.

### Impact Explanation
This is the same failure category as the delegation-bloat report: state that should have been cleaned up alongside the "burned" object (the deleted account) instead lingers and continues to be processed. Concretely:
- Storage bloat/free storage: `PromiseYieldReceipt`/`PromiseYieldStatus`/`YieldIdToDataId`/`DataIdToYieldId` entries for a deleted account are never billed to any account's `storage_usage` (the account record backing them is gone), and a new `ReceivedData` entry gets written for a nonexistent account when the stale timeout/resume finally fires — persistent state growth that nobody pays storage stake for.
- Wasted gas/compute: shards keep draining `PromiseYieldTimeout` queue entries, building `PromiseResume` receipts, and running `apply_action_receipt`/`check_account_existence` failure paths for accounts that no longer exist, exactly analogous to the wasted `removeDelegation` gas cost in the original report.
- Bloat to shared queues: unlike the C4 case (per-token delegation array capped at 500), here the affected structure is the shard-global `PromiseYieldTimeout` queue that every account's yields flow through, so orphaned entries add to a queue walked by `resolve_promise_yield_timeouts` for the whole shard on every applicable block until they expire.

This does not enable direct token theft/inflation, so it is best characterized as a low/medium-severity storage/gas-accounting hygiene bug, matching the original report's own "Medium" severity and the judge's note that no direct exploit path beyond degraded functioning was shown.

### Likelihood Explanation
Reaching this requires only ordinary, permissionless actions from any account owner: call a contract method that performs `promise_yield_create` (or `promise_yield_create_with_id`), then submit a `DeleteAccount` action for the same account before the yield resumes or times out. Both are standard, unprivileged transactions available to any user; no validator or network-layer capability is needed. The condition is not currently guarded anywhere in `validate_delete_action` or `action_delete_account`.

### Recommendation
Before allowing `action_delete_account` to proceed (or as part of `remove_account`), scan and remove any `PromiseYieldReceipt`, `PromiseYieldStatus`, `YieldIdToDataId`, and `DataIdToYieldId` entries scoped to `account_id`, mirroring how `remove_account` already sweeps `AccessKey`/`GasKeyNonce`/`ContractData` prefixes. Since `PromiseYieldTimeout` queue entries are indexed by a shard-global counter rather than by account, either mark/skip timeout entries whose target account no longer exists in `resolve_promise_yield_timeouts` (check `get_account` before synthesizing a `PromiseResume`), or reject `DeleteAccount` outright when a pending `PromiseYieldStatus`/`PromiseYieldReceipt` still exists for the account (similar in spirit to the existing gas-key-balance and storage-usage-cap pre-deletion checks in `action_delete_account`).

### Proof of Concept
Conceptual sequence (not independently executed, but each step is directly supported by the cited code paths):
1. Account `alice` deploys a contract and calls a method that invokes `promise_yield_create`, producing `TrieKey::PromiseYieldReceipt{alice, data_id}` and `TrieKey::PromiseYieldStatus{alice, data_id}` plus a `PromiseYieldTimeout` queue entry (`runtime/runtime/src/function_call.rs:160-169`, `runtime/runtime/src/ext.rs:353-369`).
2. Before the yield is resumed, `alice` submits a transaction whose final (and only) action is `DeleteAccount{beneficiary_id: bob}`. `validate_delete_action` only checks `beneficiary_id` validity (`runtime/runtime/src/action_validation.rs:399-403`); `action_delete_account` checks storage-usage cap and gas-key balances but not pending yields, then calls `remove_account`, which deletes `Account`/`ContractCode`/`AccessKey`/`ContractData` but leaves `PromiseYieldReceipt`/`PromiseYieldStatus` untouched (`core/store/src/utils/mod.rs:505-553`, `runtime/runtime/src/actions.rs:314-390`).
3. `alice` account no longer exists, yet its `PromiseYieldReceipt`/`PromiseYieldStatus` and the shard's `PromiseYieldTimeout` entry referencing `alice` persist in the trie.
4. When the timeout height arrives, `resolve_promise_yield_timeouts` finds the queue entry, sees the `PromiseYieldReceipt` key still present, and forwards a `PromiseResume{data:None}` receipt to `alice` (`runtime/runtime/src/lib.rs:3046-3097`).
5. `process_receipt` processes the `PromiseResume`, removes the stale `PromiseYieldReceipt`/`PromiseYieldStatus`, writes a fresh `ReceivedData` entry keyed to `alice` (a deleted account), and invokes `apply_action_receipt` for the parked yield receipt, which then fails with `AccountDoesNotExist` inside `check_account_existence` — after the wasted trie writes/removals and fee/compute accounting have already run (`runtime/runtime/src/lib.rs:1500-1562`, `853-854`; `runtime/runtime/src/actions.rs:787-855`).

I was not able to fully verify within the available context whether `set_received_data`'s trie write for a nonexistent account is later reconciled/removed by some other cleanup path, or whether stateless-validation/state-witness limits catch this indirectly (e.g., via `EnforcePerReceiptStorageProofLimit`); this would need to be confirmed by tracing `set_received_data`, `ReceivedData` lifecycle, and witness-size accounting further, which was outside the scope of the available index snippets.

### Citations

**File:** core/store/src/utils/mod.rs (L181-198)
```rust
// Enqueues given timeout to the PromiseYield timeout queue
pub fn enqueue_promise_yield_timeout(
    state_update: &mut TrieUpdate,
    promise_yield_indices: &mut PromiseYieldIndices,
    account_id: AccountId,
    data_id: CryptoHash,
    expires_at: BlockHeight,
) {
    set(
        state_update,
        TrieKey::PromiseYieldTimeout { index: promise_yield_indices.next_available_index },
        &PromiseYieldTimeout { account_id, data_id, expires_at },
    );
    promise_yield_indices.next_available_index = promise_yield_indices
        .next_available_index
        .checked_add(1)
        .expect("Next available index for PromiseYield timeout queue exceeded the integer limit");
}
```

**File:** core/store/src/utils/mod.rs (L505-553)
```rust
pub fn remove_account(
    state_update: &mut TrieUpdate,
    account_id: &AccountId,
) -> Result<RemoveAccountResult, StorageError> {
    state_update.remove(TrieKey::Account { account_id: account_id.clone() });
    state_update.remove(TrieKey::ContractCode { account_id: account_id.clone() });

    let mut gas_key_nonce_count: usize = 0;
    let mut gas_key_nonce_total_key_bytes: usize = 0;

    // Removing access keys and gas key nonces
    let lock = state_update.trie().lock_for_iter();
    let mut keys_to_remove: Vec<TrieKey> = Vec::new();
    for raw_key in state_update
        .locked_iter(&trie_key_parsers::get_raw_prefix_for_access_keys(account_id), &lock)?
    {
        let raw_key = raw_key?;
        let key_handle = trie_key_parsers::parse_key_handle_from_access_key_key(
            &raw_key, account_id,
        )
        .map_err(|_e| {
            StorageError::StorageInconsistentState(
                "Can't parse key handle from raw key for AccessKey".to_string(),
            )
        })?;
        let nonce_index =
            trie_key_parsers::parse_nonce_index_from_gas_key_key(&raw_key, account_id, &key_handle)
                .map_err(|_e| {
                    StorageError::StorageInconsistentState(
                        "Can't parse nonce index from raw key for AccessKey".to_string(),
                    )
                })?;
        if let Some(index) = nonce_index {
            gas_key_nonce_count += 1;
            gas_key_nonce_total_key_bytes += raw_key.len();
            keys_to_remove.push(TrieKey::gas_key_nonce(
                account_id.clone(),
                key_handle.clone(),
                index,
            ));
        } else {
            keys_to_remove.push(TrieKey::access_key(account_id.clone(), key_handle.clone()));
        }
    }
    drop(lock);

    for trie_key in keys_to_remove {
        state_update.remove(trie_key);
    }
```

**File:** core/primitives/src/trie_key.rs (L87-102)
```rust
    /// All columns except those used for the delayed receipts queue, the yielded promises
    /// queue, and the outgoing receipts buffer, which are global state for the shard.
    pub const COLUMNS_WITH_ACCOUNT_ID_IN_KEY: [(u8, &str); 12] = [
        (ACCOUNT, "Account"),
        (CONTRACT_CODE, "ContractCode"),
        (ACCESS_KEY, "AccessKey"),
        (RECEIVED_DATA, "ReceivedData"),
        (POSTPONED_RECEIPT_ID, "PostponedReceiptId"),
        (PENDING_DATA_COUNT, "PendingDataCount"),
        (POSTPONED_RECEIPT, "PostponedReceipt"),
        (CONTRACT_DATA, "ContractData"),
        (PROMISE_YIELD_RECEIPT, "PromiseYieldReceipt"),
        (PROMISE_YIELD_STATUS, "PromiseYieldStatus"),
        (YIELD_ID_TO_DATA_ID, "YieldIdToDataId"),
        (DATA_ID_TO_YIELD_ID, "DataIdToYieldId"),
    ];
```

**File:** core/primitives/src/trie_key.rs (L242-247)
```rust
    /// Used to store the postponed promise yield receipt `primitives::receipt::Receipt`
    /// for a given receiver's `AccountId` and a given `data_id`.
    PromiseYieldReceipt {
        receiver_id: AccountId,
        data_id: CryptoHash,
    } = col::PROMISE_YIELD_RECEIPT,
```

**File:** runtime/runtime/src/actions.rs (L314-390)
```rust
pub(crate) fn action_delete_account(
    state_update: &mut TrieUpdate,
    account: &mut Option<Account>,
    actor_id: &mut AccountId,
    receipt: &Receipt,
    result: &mut ActionResult,
    account_id: &AccountId,
    delete_account: &DeleteAccountAction,
    config: &RuntimeConfig,
    current_protocol_version: ProtocolVersion,
) -> Result<(), StorageError> {
    let account_ref = account.as_ref().unwrap();
    let account_storage_usage = if ProtocolFeature::FixDeleteAccountGlobalContractStorageUsage
        .enabled(current_protocol_version)
    {
        let contract_storage = get_contract_storage_usage(state_update, account_id, account_ref)?;
        account_ref.storage_usage().saturating_sub(contract_storage)
    } else {
        // Legacy behavior: only subtracts local contract code, misses the
        // global contract identifier overhead.
        let account_storage_usage = account_ref.storage_usage();
        let code_len = get_code_len_or_default(
            state_update,
            account_id.clone(),
            account_ref.local_contract_hash().unwrap_or_default(),
        )?;
        debug_assert!(
            code_len == 0 || account_storage_usage > code_len,
            "account storage usage should be larger than code size. storage usage: {}, code size: {}",
            account_storage_usage,
            code_len
        );
        account_storage_usage.saturating_sub(code_len)
    };
    if account_storage_usage > Account::MAX_ACCOUNT_DELETION_STORAGE_USAGE {
        result.result =
            Err(ActionErrorKind::DeleteAccountWithLargeState { account_id: account_id.clone() }
                .into());
        return Ok(());
    }
    let gas_key_balance_to_burn = compute_gas_key_balance_sum(state_update, account_id)?;
    if gas_key_balance_to_burn > GasKeyInfo::MAX_BALANCE_TO_BURN {
        result.result = Err(ActionErrorKind::GasKeyBalanceTooHigh {
            account_id: account_id.clone(),
            public_key: None,
            balance: gas_key_balance_to_burn,
        }
        .into());
        return Ok(());
    }
    // We use current amount as a pay out to beneficiary.
    let account_balance = account_ref.amount();
    if account_balance > Balance::ZERO {
        result
            .new_receipts
            .push(Receipt::new_balance_refund(&delete_account.beneficiary_id, account_balance));
    }
    let remove_result = remove_account(state_update, account_id)?;
    result.tokens_burnt =
        result.tokens_burnt.checked_add(gas_key_balance_to_burn).ok_or_else(|| {
            StorageError::StorageInconsistentState("tokens_burnt overflow".to_string())
        })?;
    if remove_result.gas_key_nonce_count > 0 {
        let compute = storage_removes_compute(
            &config.wasm_config.ext_costs,
            remove_result.gas_key_nonce_count,
            remove_result.gas_key_nonce_total_key_bytes,
            AccessKey::NONCE_VALUE_LEN * remove_result.gas_key_nonce_count,
        );
        result.compute_usage = safe_add_compute(result.compute_usage, compute).map_err(|_| {
            StorageError::StorageInconsistentState("compute_usage overflow".to_string())
        })?;
    }
    *actor_id = receipt.predecessor_id().clone();
    *account = None;
    Ok(())
}
```

**File:** runtime/runtime/src/actions.rs (L787-855)
```rust
pub(crate) fn check_account_existence(
    action: &Action,
    account: &Option<Account>,
    account_id: &AccountId,
    config: &RuntimeConfig,
    implicit_account_creation_eligible: bool,
) -> Result<(), ActionError> {
    match action {
        Action::CreateAccount(_) => {
            if account.is_some() {
                return Err(ActionErrorKind::AccountAlreadyExists {
                    account_id: account_id.clone(),
                }
                .into());
            } else {
                if account_is_implicit(account_id, config.wasm_config.eth_implicit_accounts) {
                    // If the account doesn't exist and it's implicit, then you
                    // should only be able to create it using single transfer action.
                    // Because you should not be able to add another access key to the account in
                    // the same transaction.
                    // Otherwise you can hijack an account without having the private key for the
                    // public key. We've decided to make it an invalid transaction to have any other
                    // actions on the implicit hex accounts.
                    // The easiest way is to reject the `CreateAccount` action.
                    // See https://github.com/nearprotocol/NEPs/pull/71
                    return Err(ActionErrorKind::OnlyImplicitAccountCreationAllowed {
                        account_id: account_id.clone(),
                    }
                    .into());
                }
            }
        }
        Action::Transfer(_) => {
            if account.is_none() {
                return check_transfer_to_nonexisting_account(
                    config,
                    account_id,
                    implicit_account_creation_eligible,
                );
            }
        }
        Action::DeterministicStateInit(_) => {
            // Existing and non existing is valid for DeterministicStateInit.
            // Does not exist => The account will be created by the action.
            // Does exist => Nothing happens but the receipt is not aborted to
            // allow optional init before other actions.
        }
        Action::DeployContract(_)
        | Action::FunctionCall(_)
        | Action::Stake(_)
        | Action::AddKey(_)
        | Action::DeleteKey(_)
        | Action::DeleteAccount(_)
        | Action::Delegate(_)
        | Action::DelegateV2(_)
        | Action::DeployGlobalContract(_)
        | Action::UseGlobalContract(_)
        | Action::TransferToGasKey(_)
        | Action::WithdrawFromGasKey(_) => {
            if account.is_none() {
                return Err(ActionErrorKind::AccountDoesNotExist {
                    account_id: account_id.clone(),
                }
                .into());
            }
        }
    };
    Ok(())
}
```

**File:** runtime/runtime/src/action_validation.rs (L399-403)
```rust
fn validate_delete_action(action: &DeleteAccountAction) -> Result<(), ActionsValidationError> {
    validate_action_account_id(&action.beneficiary_id)?;

    Ok(())
}
```

**File:** runtime/runtime/src/function_call.rs (L151-169)
```rust
    if execution_succeeded {
        // Fetch metadata for PromiseYield timeout queue
        let mut promise_yield_indices = get_promise_yield_indices(state_update)?;
        let initial_promise_yield_indices = promise_yield_indices.clone();

        let mut new_receipts: Vec<_> = receipt_manager
            .action_receipts
            .into_iter()
            .map(|receipt| {
                // If the newly created receipt is a PromiseYield, enqueue a timeout for it
                if receipt.is_promise_yield {
                    enqueue_promise_yield_timeout(
                        state_update,
                        &mut promise_yield_indices,
                        account_id.clone(),
                        receipt.input_data_ids[0],
                        apply_state.block_height
                            + config.wasm_config.limit_config.yield_timeout_length_in_blocks,
                    );
```

**File:** runtime/runtime/src/lib.rs (L853-854)
```rust
        let mut account = get_account(state_update, account_id)?;
        let account_did_not_exist = account.is_none();
```

**File:** runtime/runtime/src/lib.rs (L1500-1562)
```rust
            VersionedReceiptEnum::PromiseResume(data_receipt) => {
                if data_receipt.data.is_none() {
                    // This is a timeout resume. Check the status to see if the receipt has been resumed.
                    let status =
                        get_promise_yield_status(state_update, account_id, data_receipt.data_id)?;
                    if status == Some(PromiseYieldStatus::ResumeInitiated) {
                        // A non-timeout resume receipt has been sent, cancel the timeout.
                        return Ok(None);
                    }
                }

                // Received a new PromiseResume receipt delivering input data for a PromiseYield.
                // It is guaranteed that the PromiseYield has exactly one input data dependency
                // and that it arrives first, so we can simply find and execute it.
                if let Some(yield_receipt) =
                    get_promise_yield_receipt(state_update, account_id, data_receipt.data_id)?
                {
                    // Remove the receipt from the state
                    remove_promise_yield_receipt(state_update, account_id, data_receipt.data_id);

                    // Clear the PromiseYield status
                    remove_promise_yield_status(state_update, account_id, data_receipt.data_id);

                    // Clean up yield_id <-> data_id mappings if this was created by yield_create_with_id
                    if ProtocolFeature::YieldWithId.enabled(apply_state.current_protocol_version) {
                        if let Some(yield_id) = get_yield_id_for_data_id(
                            state_update,
                            account_id,
                            data_receipt.data_id,
                        )? {
                            remove_yield_id_mappings(
                                state_update,
                                account_id,
                                yield_id,
                                data_receipt.data_id,
                            );
                        }
                    }

                    // Save the data into the state keyed by the data_id
                    set_received_data(
                        state_update,
                        account_id.clone(),
                        data_receipt.data_id,
                        &ReceivedData { data: data_receipt.data.clone() },
                    );

                    // Execute the PromiseYield receipt. It will read the input data and clean it
                    // up from the state.
                    return self
                        .apply_action_receipt(
                            state_update,
                            apply_state,
                            pipeline_manager,
                            &yield_receipt,
                            receipt_sink,
                            instant_receipts,
                            validator_proposals,
                            stats,
                            epoch_info_provider,
                            receipt_to_tx,
                        )
                        .map(Some);
```

**File:** runtime/runtime/src/lib.rs (L3009-3098)
```rust
fn resolve_promise_yield_timeouts(
    processing_state: &mut ApplyProcessingReceiptState,
    receipt_sink: &mut ReceiptSink,
    compute_limit: u64,
) -> Result<ResolvePromiseYieldTimeoutsResult, RuntimeError> {
    let mut state_update = &mut processing_state.state_update;
    let total = &mut processing_state.total;
    let apply_state = &processing_state.apply_state;

    let mut promise_yield_indices: PromiseYieldIndices =
        get(state_update, &TrieKey::PromiseYieldIndices)?.unwrap_or_default();
    let initial_promise_yield_indices = promise_yield_indices.clone();
    let mut new_receipt_index: usize = 0;

    let mut processed_yield_timeouts = vec![];
    let yield_processing_start = std::time::Instant::now();
    while promise_yield_indices.first_index < promise_yield_indices.next_available_index {
        if total.compute >= compute_limit || state_update.trie.check_proof_size_limit_exceed() {
            break;
        }

        let queue_entry_key =
            TrieKey::PromiseYieldTimeout { index: promise_yield_indices.first_index };

        let queue_entry =
            get::<PromiseYieldTimeout>(state_update, &queue_entry_key)?.ok_or_else(|| {
                StorageError::StorageInconsistentState(format!(
                    "PromiseYield timeout queue entry #{} should be in the state",
                    promise_yield_indices.first_index
                ))
            })?;

        // Queue entries are ordered by expires_at
        if queue_entry.expires_at > apply_state.block_height {
            break;
        }

        // Check if the yielded promise still needs to be resolved
        let promise_yield_key = TrieKey::PromiseYieldReceipt {
            receiver_id: queue_entry.account_id.clone(),
            data_id: queue_entry.data_id,
        };
        if state_update.contains_key(&promise_yield_key, AccessOptions::DEFAULT)? {
            let new_receipt_id = create_receipt_id_from_receipt_id(
                &queue_entry.data_id,
                apply_state.block_height,
                new_receipt_index,
            );
            new_receipt_index += 1;

            // Create a PromiseResume receipt to resolve the timed-out yield.
            let resume_receipt = Receipt::V0(ReceiptV0 {
                predecessor_id: queue_entry.account_id.clone(),
                receiver_id: queue_entry.account_id.clone(),
                receipt_id: new_receipt_id,
                receipt: ReceiptEnum::PromiseResume(DataReceipt {
                    data_id: queue_entry.data_id,
                    data: None,
                }),
            });

            // Record a ReceiptToTx entry for the new resume receipt. The parent is the
            // yield receipt that is being timed out.
            if processing_state.apply_state.save_receipt_to_tx {
                let yield_receipt: Receipt = get_pure(state_update, &promise_yield_key)?
                    .expect("promise yield receipt should exist since contains_key was true");
                processing_state.receipt_to_tx.push((
                    new_receipt_id,
                    ReceiptToTxInfo::V1(ReceiptToTxInfoV1 {
                        origin: ReceiptOrigin::FromReceipt(ReceiptOriginReceipt {
                            parent_receipt_id: *yield_receipt.receipt_id(),
                            parent_predecessor_id: yield_receipt.predecessor_id().clone(),
                        }),
                        receiver_account_id: queue_entry.account_id.clone(),
                        shard_id: processing_state.apply_state.shard_id,
                    }),
                ));
            }

            // The receipt is destined for the local shard and will be placed in the outgoing
            // receipts buffer. It is possible that there is already an outgoing receipt resolving
            // this yield if `yield_resume` was invoked by some receipt which was processed in
            // the current chunk. The ordering will be maintained because the receipts are
            // destined for the same shard; the timeout will be processed second and discarded.
            receipt_sink.forward_or_buffer_receipt(
                resume_receipt,
                apply_state,
                &mut state_update,
            )?;
        }
```
