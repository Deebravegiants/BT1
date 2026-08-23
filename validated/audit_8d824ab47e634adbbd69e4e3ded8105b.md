## Analysis

I found a concrete structural analog to the C4 report's bug class: an entity that is "removed" while a nested, key-associated sub-record tied to it is left behind in storage, and that sub-record is later reactivated as if it were fresh when the entity's identifier is reused.

`remove_account` in `core/store/src/utils/mod.rs` is the function invoked by `action_delete_account` to purge an account's state from the trie. It explicitly removes `TrieKey::Account`, `TrieKey::ContractCode`, all `AccessKey`/gas-key-nonce entries under the account's prefix, and all `ContractData` entries under the account's prefix. [1](#0-0) [2](#0-1) 

However, several other trie namespaces that are also keyed by `receiver_id: AccountId` are never touched by `remove_account`: `TrieKey::ReceivedData`, `TrieKey::PostponedReceiptId`, `TrieKey::PendingDataCount`, `TrieKey::PostponedReceipt`, `TrieKey::PromiseYieldReceipt`, and `TrieKey::PromiseYieldStatus`. [3](#0-2) 
`action_delete_account` (the caller) only checks storage-usage size caps and gas-key balance-to-burn limits before calling `remove_account`; it performs no check for outstanding postponed receipts, pending data counts, or unresolved promise-yields addressed to the account being deleted. [4](#0-3) 

These queues are populated independently of account existence: when an `ActionReceipt` with unmet `input_data_ids` arrives at a receiver, the runtime records a `PostponedReceiptId`/`PendingDataCount`/`PostponedReceipt` under that receiver's `AccountId`; when a matching `DataReceipt` later arrives, the runtime looks up `PostponedReceiptId` purely by `(receiver_id, data_id)`, decrements the pending count, and — once it hits zero — fetches and *executes* the stored `PostponedReceipt` against whatever account currently exists under that `receiver_id`. [5](#0-4)  Nothing in this lookup path checks whether the account that originally received the postponed receipt is the same "incarnation" as the account now present at that `AccountId` — the check is keyed solely on the account-id string and `data_id`, both of which survive account deletion/recreation unchanged.

This exactly mirrors the report's pattern: a "removal" operation (`_removeAsset`/`action_delete_account`) clears the top-level record but leaves a nested, key-addressed sub-structure (`feederPrice`/`PostponedReceipt` & friends) intact; later, when the identifier is reused (asset re-added / account recreated with the same `account_id`), the stale sub-structure is picked up and treated as valid current data (`_combine`/`process_receipt`), because the "freshness" check (timestamp+expiration / pending-count reaching zero) doesn't account for the intervening removal.

The `TrieKey` documentation itself independently groups these six columns together as "columns with account id in key" that are conceptually tied to account lifetime, reinforcing that they are meant to be account-scoped state, yet `remove_account` — the single function responsible for wiping an account's footprint — does not clear them. [6](#0-5) 

## Uncertainties

- I could not find, within the indexed portion of the codebase, an explicit runtime check that rejects `DeleteAccount` when the account still has outstanding postponed receipts, pending data, or unresolved promise-yields. If such a guard exists elsewhere and was not surfaced by search, it would neutralize the "stale postponed receipt executes against a recreated account" impact vector (though the storage-leak aspect — orphaned trie rows never charged to any account and never garbage-collected — would still stand, since GC operates on block/epoch height, not on account lifecycle, per `chain/client/src/gc_actor.rs`).
- I did not find code that walks these six namespaces during account deletion, garbage collection, or resharding to reclaim orphaned entries; the resharding tests I found (`slow_test_resharding_v3_promise_yield_indices_gc_correctness`, `slow_test_resharding_v3_delayed_receipts_gc_correctness`) concern shard-boundary queue integrity, not account-deletion cleanup, so they don't validate this specific path.
- Given index-size limits, I was not able to fully trace every call site that reads `PromiseYieldReceipt`/`PromiseYieldStatus` or `PostponedReceipt` to confirm there is no secondary account-existence check added elsewhere. Confirming end-to-end exploitability (e.g., constructing a reproducible sequence: postponed receipt pending → `DeleteAccount` → `CreateAccount` (same id) → matching `DataReceipt` arrives → stale receipt executes) would require running the actual runtime apply tests, which is out of scope for this read-only analysis. If the user wants this validated with a concrete failing test, a Devin session with terminal/test access would be needed to write and run a `runtime/runtime/src/tests/apply.rs`-style repro.

### Citations

**File:** core/store/src/utils/mod.rs (L504-510)
```rust
/// Removes account, code and all access keys and gas keys associated to it.
pub fn remove_account(
    state_update: &mut TrieUpdate,
    account_id: &AccountId,
) -> Result<RemoveAccountResult, StorageError> {
    state_update.remove(TrieKey::Account { account_id: account_id.clone() });
    state_update.remove(TrieKey::ContractCode { account_id: account_id.clone() });
```

**File:** core/store/src/utils/mod.rs (L551-574)
```rust
    for trie_key in keys_to_remove {
        state_update.remove(trie_key);
    }

    // Removing contract data
    let lock = state_update.trie().lock_for_iter();
    let data_keys = state_update
        .locked_iter(&trie_key_parsers::get_raw_prefix_for_contract_data(account_id, &[]), &lock)?
        .map(|raw_key| {
            trie_key_parsers::parse_data_key_from_contract_data_key(&raw_key?, account_id)
                .map_err(|_e| {
                    StorageError::StorageInconsistentState(
                        "Can't parse data key from raw key for ContractData".to_string(),
                    )
                })
                .map(Vec::from)
        })
        .collect::<Result<Vec<_>, _>>()?;
    drop(lock);

    for key in data_keys {
        state_update.remove(TrieKey::ContractData { account_id: account_id.clone(), key });
    }
    Ok(RemoveAccountResult { gas_key_nonce_count, gas_key_nonce_total_key_bytes })
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

**File:** core/primitives/src/trie_key.rs (L192-247)
```rust
    /// Used to store `primitives::receipt::ReceivedData` struct for a given receiver's `AccountId`
    /// of `DataReceipt` and a given `data_id` (the unique identifier for the data).
    /// NOTE: This is one of the input data for some action receipt.
    /// The action receipt might be still not be received or requires more pending input data.
    ReceivedData {
        receiver_id: AccountId,
        data_id: CryptoHash,
    } = col::RECEIVED_DATA,
    /// Used to store receipt ID `primitives::hash::CryptoHash` for a given receiver's `AccountId`
    /// of the receipt and a given `data_id` (the unique identifier for the required input data).
    /// NOTE: This receipt ID indicates the postponed receipt. We store `receipt_id` for performance
    /// purposes to avoid deserializing the entire receipt.
    PostponedReceiptId {
        receiver_id: AccountId,
        data_id: CryptoHash,
    } = col::POSTPONED_RECEIPT_ID,
    /// Used to store the number of still missing input data `u32` for a given receiver's
    /// `AccountId` and a given `receipt_id` of the receipt.
    PendingDataCount {
        receiver_id: AccountId,
        receipt_id: CryptoHash,
    } = col::PENDING_DATA_COUNT,
    /// Used to store the postponed receipt `primitives::receipt::Receipt` for a given receiver's
    /// `AccountId` and a given `receipt_id` of the receipt.
    PostponedReceipt {
        receiver_id: AccountId,
        receipt_id: CryptoHash,
    } = col::POSTPONED_RECEIPT,
    /// Used to store indices of the delayed receipts queue (`node-runtime::DelayedReceiptIndices`).
    /// NOTE: It is a singleton per shard.
    DelayedReceiptIndices = col::DELAYED_RECEIPT_OR_INDICES,
    /// Used to store a delayed receipt `primitives::receipt::Receipt` for a given index `u64`
    /// in a delayed receipt queue. The queue is unique per shard.
    DelayedReceipt {
        index: u64,
    } = 8,
    /// Used to store a key-value record `Vec<u8>` within a contract deployed on a given `AccountId`
    /// and a given key.
    ContractData {
        account_id: AccountId,
        key: Vec<u8>,
    } = col::CONTRACT_DATA,
    /// Used to store head and tail indices of the PromiseYield timeout queue.
    /// NOTE: It is a singleton per shard.
    PromiseYieldIndices = col::PROMISE_YIELD_INDICES,
    /// Used to store the element at given index `u64` in the PromiseYield timeout queue.
    /// The queue is unique per shard.
    PromiseYieldTimeout {
        index: u64,
    } = col::PROMISE_YIELD_TIMEOUT,
    /// Used to store the postponed promise yield receipt `primitives::receipt::Receipt`
    /// for a given receiver's `AccountId` and a given `data_id`.
    PromiseYieldReceipt {
        receiver_id: AccountId,
        data_id: CryptoHash,
    } = col::PROMISE_YIELD_RECEIPT,
```

**File:** runtime/runtime/src/actions.rs (L314-371)
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
```

**File:** runtime/runtime/src/lib.rs (L1396-1444)
```rust
                // given data_id.
                // If we don't have a postponed receipt yet, we don't need to do anything for now.
                if let Some(receipt_id) = get(
                    state_update,
                    &TrieKey::PostponedReceiptId {
                        receiver_id: account_id.clone(),
                        data_id: data_receipt.data_id,
                    },
                )? {
                    // There is already a receipt that is awaiting for the just received data.
                    // Removing this pending data_id for the receipt from the state.
                    state_update.remove(TrieKey::PostponedReceiptId {
                        receiver_id: account_id.clone(),
                        data_id: data_receipt.data_id,
                    });
                    // Checking how many input data items is pending for the receipt.
                    let pending_data_count: u32 = get(
                        state_update,
                        &TrieKey::PendingDataCount { receiver_id: account_id.clone(), receipt_id },
                    )?
                    .ok_or_else(|| {
                        StorageError::StorageInconsistentState(
                            "pending data count should be in the state".to_string(),
                        )
                    })?;
                    if pending_data_count == 1 {
                        // It was the last input data pending for this receipt. We'll cleanup
                        // some receipt related fields from the state and execute the receipt.

                        // Removing pending data count from the state.
                        state_update.remove(TrieKey::PendingDataCount {
                            receiver_id: account_id.clone(),
                            receipt_id,
                        });
                        // Fetching the receipt itself.
                        let ready_receipt =
                            get_postponed_receipt(state_update, account_id, receipt_id)?
                                .ok_or_else(|| {
                                    StorageError::StorageInconsistentState(
                                        "pending receipt should be in the state".to_string(),
                                    )
                                })?;
                        // Removing the receipt from the state.
                        remove_postponed_receipt(state_update, account_id, receipt_id);
                        // Executing the receipt. It will read all the input data and clean it up
                        // from the state.
                        return self
                            .apply_action_receipt(
                                state_update,
```
