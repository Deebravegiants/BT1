### Title
Removal-witness metering (`record_key_removal`) is scoped only to `TrieKey::ContractData`, letting unprivileged `DeleteKey`/`DeleteAccount` actions remove `AccessKey`/`Account`/gas-key-nonce trie entries without the compensating upper-bound charge - (`core/store/src/trie/update.rs`)

### Summary
`TrieUpdate::remove` only invokes `TrieRecorder::record_key_removal()` (which adds a fixed 2000-byte buffer to `recorded_storage_size_upper_bound`) when the removed key matches `TrieKey::ContractData`. Ordinary account holders can trigger removals of `TrieKey::AccessKey`, `TrieKey::Account`, and gas-key-nonce entries via `DeleteKey`/`DeleteAccount` actions, which go through the exact same `TrieUpdate::remove` code path but never receive this compensating charge.

### Finding Description
`TrieUpdate::remove` explicitly gates the extra-charge logic to one `TrieKey` variant: [1](#0-0) 

The comment explains the rationale (from near/nearcore#10890): removing a trie entry can trigger branch/extension-node restructuring at commit time that isn't reflected in the nodes actually read/recorded during execution, so a fixed per-removal buffer is added to the *upper bound* estimate to stay safe. This restructuring effect is a property of the underlying Patricia-Merkle trie algorithm and does not depend on which logical `TrieKey` column is being removed - yet the code only applies the buffer for `ContractData`.

Both `AccessKey` and `Account`/gas-key-nonce removals reach `TrieUpdate::remove` through the same runtime helpers, invoked from ordinary, attacker-controlled actions:
- `remove_access_key` / `remove_gas_key_nonce` / `remove_account`, called from `delete_regular_key`, `delete_gas_key` (triggered by `Action::DeleteKey`), and `remove_account` (triggered by `Action::DeleteAccount`): [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

The witness/compute size guard consulted during execution (`recorded_storage_size_upper_bound` / `check_proof_size_limit_exceed`) is backed by `TrieRecorder`, whose `upper_bound_size` only receives the +2000 bump from `record_key_removal`, which is unreachable for non-`ContractData` removals: [6](#0-5) [7](#0-6) 

The runtime relies on `recorded_storage_size_upper_bound()` (not the raw `recorded_storage_size()`) precisely because it is documented as covering these corner cases: [8](#0-7) 

Since `AccessKey`/`Account`/gas-key-nonce removals bypass the buffer entirely, the reported upper bound can under-represent the true post-commit proof-size growth for these removals, breaking the stated metering-completeness invariant for this class of key.

### Impact Explanation
This is a metering-completeness bug: chunk-witness/storage-proof growth from `AccessKey`/`Account`/gas-key-nonce removals is not fully charged before/at the time of the action, unlike `ContractData` removals which received an explicit fix for the same underlying issue (near/nearcore#10890). In the worst case this can cause `recorded_storage_size_upper_bound()` to underestimate the true finalized `PartialStorage` size, risking chunk witness size exceeding the intended metered/charged bound - a resource-accounting/consensus-adjacent risk class (unbounded/underpriced resource use), scoped to state-witness generation rather than direct fund loss.

### Likelihood Explanation
Reachable by any unprivileged account holder without special privileges: create multiple `AddKey` actions (regular or gas keys) on one's own account (bounded by normal storage-staking costs), then submit `DeleteKey` actions or a single `DeleteAccount` action. `DeleteAccount` in particular iterates and removes every access key and gas-key nonce for the account in one receipt via `remove_account`, none of which are charged the removal buffer. Note two partially mitigating factors present in the code: (1) `DeleteAccount` is capped by `Account::MAX_ACCOUNT_DELETION_STORAGE_USAGE` on total account storage usage [9](#0-8) , which bounds how many keys can be batch-removed this way; and (2) `DeleteKey` actions are limited by the max actions permitted per transaction/receipt. These bounds reduce (but do not eliminate) the achievable amplification, and I could not verify the exact numeric value of `MAX_ACCOUNT_DELETION_STORAGE_USAGE` in this pass to quantify the worst-case number of keys removable in a single uncharged batch.

### Recommendation
Change the guard in `TrieUpdate::remove` to charge `record_key_removal()` for all attacker-reachable, non-runtime-internal removal kinds - i.e., include `TrieKey::AccessKey`, `TrieKey::Account`, and gas-key-nonce keys (or invert the logic to charge by default and only exempt trusted/internal runtime removals) - so the upper-bound estimate remains a true upper bound regardless of which trie column is removed.

### Proof of Concept
Unit/integration test plan (extending the existing recording tests in `core/store/src/trie/trie_recording.rs`):
1. Build a `TrieUpdate` with a recorder (`trie.recording_reads_new_recorder()`), populate an account with hundreds of `AccessKey`/gas-key-nonce entries.
2. Call `remove_account` (or repeated `remove_access_key`) to remove all of them in one update, matching the code path used by `action_delete_account`/`action_delete_key`.
3. Record `recorded_storage_size_upper_bound()` before `finalize()`.
4. Call `trie.update(...)`/`finalize()` to produce the final `TrieChanges`, and separately reconstruct the true `PartialStorage` size after commit-time restructuring (via `recorded_storage()`/`recorded_trie_changes`).
5. Assert `recorded_storage_size_upper_bound() >= actual_final_proof_size`; the test is expected to demonstrate cases where this invariant is violated for `AccessKey`/`Account` removals (in contrast to an analogous `ContractData`-removal test, which should hold because of the existing +2000-byte charge).

### Citations

**File:** core/store/src/trie/update.rs (L169-182)
```rust
    pub fn remove(&mut self, trie_key: TrieKey) {
        // We count removals performed by the contracts and charge extra for them.
        // A malicious contract could generate a lot of storage proof by a removal,
        // charging extra provides a safe upper bound. (https://github.com/near/nearcore/issues/10890)
        // This only applies to removals performed by the contracts. Removals performed
        // by the runtime are assumed to be non-malicious and we don't charge extra for them.
        if let Some(recorder) = &self.trie.recorder {
            if matches!(trie_key, TrieKey::ContractData { .. }) {
                recorder.record_key_removal();
            }
        }

        self.prospective.insert(trie_key.to_vec(), TrieKeyValueUpdate { trie_key, value: None });
    }
```

**File:** core/store/src/utils/mod.rs (L394-409)
```rust
pub fn remove_access_key(
    state_update: &mut TrieUpdate,
    account_id: AccountId,
    public_key: PublicKey,
) {
    state_update.remove(TrieKey::access_key(account_id, public_key));
}

pub fn remove_gas_key_nonce(
    state_update: &mut TrieUpdate,
    account_id: AccountId,
    public_key: PublicKey,
    nonce_index: NonceIndex,
) {
    state_update.remove(TrieKey::gas_key_nonce(account_id, public_key, nonce_index));
}
```

**File:** core/store/src/utils/mod.rs (L486-535)
```rust
/// Removes account, code and all access keys and gas keys associated to it.
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

**File:** runtime/runtime/src/access_keys.rs (L126-146)
```rust
    remove_access_key(state_update, account_id.clone(), public_key.clone());
    account.set_storage_usage(account.storage_usage().saturating_sub(gas_key_storage_cost(
        &config.fees,
        public_key,
        access_key,
        gas_key_info.num_nonces,
    )));
    Ok(())
}

fn delete_regular_key(
    fee_config: &RuntimeFeesConfig,
    state_update: &mut TrieUpdate,
    account: &mut Account,
    account_id: &AccountId,
    public_key: &PublicKey,
    access_key: &AccessKey,
) {
    let storage_usage = access_key_storage_usage(fee_config, public_key, access_key);
    remove_access_key(state_update, account_id.clone(), public_key.clone());
    account.set_storage_usage(account.storage_usage().saturating_sub(storage_usage));
```

**File:** runtime/runtime/src/actions.rs (L299-356)
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

**File:** core/store/src/trie/trie_recording.rs (L140-146)
```rust
    pub fn record_key_removal(&self) {
        // Charge 2000 bytes for every removal
        self.upper_bound_size.fetch_add(2000, Ordering::Release).checked_add(2000).unwrap();
        // No need to check for overflows here as the `upper_bound_size` would overflow sooner than
        // this if there was an overflow.
        self.removal_counter.fetch_add(1, Ordering::Relaxed);
    }
```

**File:** core/store/src/trie/trie_recording.rs (L199-205)
```rust
    pub fn recorded_storage_size(&self) -> usize {
        self.size.load(Ordering::Acquire)
    }

    pub fn recorded_storage_size_upper_bound(&self) -> usize {
        self.upper_bound_size.load(Ordering::Acquire)
    }
```

**File:** runtime/runtime/src/ext.rs (L310-317)
```rust
    fn get_recorded_storage_size(&self) -> usize {
        // `recorded_storage_size()` doesn't provide the exact size of storage proof
        // as it doesn't cover some corner cases (see https://github.com/near/nearcore/issues/10890),
        // so we use the `upper_bound` version to estimate how much storage proof
        // could've been generated by the receipt. As long as upper bound is
        // under the limit we can be sure that the actual value is also under the limit.
        self.trie_update.trie().recorded_storage_size_upper_bound()
    }
```
