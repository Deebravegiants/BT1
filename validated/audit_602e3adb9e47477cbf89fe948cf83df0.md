Based on my research, I found one plausible analog worth flagging, but with an important caveat about unresolved uncertainty on the actual severity/exploitability.

### Title
Uncharged unbounded loop in `action_delete_account`/`remove_account` over access keys and contract data - ([File: runtime/runtime/src/actions.rs], [File: core/store/src/utils/mod.rs])

### Summary
`DeleteAccount` triggers `remove_account`, which iterates over *every* access-key trie entry and *every* `ContractData` trie entry belonging to the account and removes them one by one [1](#0-0) . Unlike the gas-key-nonce removal path, which is metered proportionally via `storage_removes_compute` based on `remove_result.gas_key_nonce_count`, the loop counts and compute charge in `action_delete_account` only account for gas-key nonces — regular access-key removal and all `ContractData` removal are not charged any compute proportional to the number of entries removed [2](#0-1) .

### Finding Description
This mirrors the dForce bug class: an unbounded, insufficiently-metered loop reachable from a single user-submitted action. The only guard rail present is `MAX_ACCOUNT_DELETION_STORAGE_USAGE = 10_000` bytes, checked against `account_storage_usage`, which is explicitly computed by subtracting *contract code* storage (`get_contract_storage_usage`/`get_code_len_or_default`) from the account's total tracked storage usage [3](#0-2) . Whether this residual `account_storage_usage` also bounds the number of `ContractData` (key/value) entries written via `storage_write`, or only bounds access-key bytes, could not be conclusively confirmed from the available context — this is the key open question for this analog.

If `account.storage_usage()` does *not* fully account for `ContractData` bytes written by the contract (or if there exist code paths where large numbers of small keys accumulate more trie overhead than the per-byte accounting reflects), an attacker-controlled contract account could accumulate many storage entries (paid for via ordinary storage staking) and then issue a single `DeleteAccount` action whose fixed `exec_fee` does not scale with the number of entries actually removed by `remove_account`'s trie walk, similar to how dForce's fixed-cost liquidation call performed unbounded per-asset iteration.

### Impact Explanation
If exploitable, this would let an account holder cause the runtime to perform work (trie iteration + N removals) whose real cost is not reflected in the gas charged for the `DeleteAccount` action, i.e., underpriced/free execution, and could degrade chunk-application performance for validators processing the receipt (potential chain slowdown under repeated abuse). This matches the "free or underpriced execution... node panic or unbounded resource use" category called out in the validation rules.

### Likelihood Explanation
Low-to-uncertain. The `MAX_ACCOUNT_DELETION_STORAGE_USAGE` cap and existing storage-staking economics (an attacker must pay ongoing per-byte storage rent to keep a large amount of `ContractData` alive) already impose real economic cost proportional to state size, which differs materially from the dForce case where markets could be entered essentially for free. I was not able to conclusively verify, given the remaining exploration budget, whether the 10,000-byte deletion cap actually bounds the number of `ContractData` entries (as opposed to only code-storage bytes), which is the deciding factor for whether this is truly unbounded.

### Recommendation
Verify precisely what `account.storage_usage()` includes relative to `ContractData` entries, and if it is possible for `ContractData` byte/entry counts to exceed what `MAX_ACCOUNT_DELETION_STORAGE_USAGE` implicitly bounds, either (a) extend `storage_removes_compute`-style metering to cover access-key and contract-data removal counts in `action_delete_account`, matching what is already done for gas-key nonces, or (b) tighten/clarify the deletion-size cap to explicitly bound total entries (not just non-contract bytes) removable in a single `DeleteAccount` action.

### Proof of Concept
Not constructed — this would require confirming, via a running node or additional source inspection (e.g. `core/primitives-core/src/account.rs` storage-usage accounting and the `storage_write` host-function accounting in `near-vm-runner`), whether `account_storage_usage` bounds `ContractData` entry counts prior to attempting a live reproduction.

**Given the unresolved uncertainty on whether the existing storage-usage/deletion-size cap already fully bounds this loop, I cannot confidently assert this is an unmitigated, concretely exploitable vulnerability** as opposed to an already-mitigated design (similar to how `ViewAccessKeyList`'s pagination/`TooManyAccessKeys` limit and the compute-limit-gated receipt processing loops already directly implement the dForce report's own recommended mitigation of capping unbounded per-account loops). All other candidate loops examined (delayed/incoming/local receipt processing, access-key listing RPC, congestion-control loops) were found to already have explicit caps or per-iteration gas/compute checks that break out before exceeding block limits [4](#0-3) [5](#0-4) .

### Citations

**File:** core/store/src/utils/mod.rs (L504-574)
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

**File:** runtime/runtime/src/actions.rs (L325-353)
```rust
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
```

**File:** runtime/runtime/src/actions.rs (L371-386)
```rust
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
```

**File:** runtime/runtime/src/lib.rs (L2485-2500)
```rust
        loop {
            if processing_state.total.compute >= compute_limit
                || processing_state.state_update.trie.check_proof_size_limit_exceed()
            {
                break;
            }

            let receipt = if let Some(receipt) = processing_state
                .delayed_receipts
                .pop(&mut processing_state.state_update, &processing_state.apply_state.config)?
            {
                receipt.into_receipt()
            } else {
                // Break loop if there are no more receipts to be processed.
                break;
            };
```

**File:** runtime/runtime/src/state_viewer/mod.rs (L243-258)
```rust
            if let Some(cap) = item_cap {
                if keys.len() as u64 >= u64::from(cap) {
                    // Page is full and at least one more key exists: emit a cursor
                    // at the last kept key so the caller can resume.
                    last_key = keys
                        .last()
                        .map(|(handle, _): &(PublicKeyHandle, AccessKey)| handle.clone());
                    break;
                }
            } else if keys.len() as u64 >= u64::from(max) {
                // Unpaginated request that exceeds the configured limit.
                return Err(errors::ViewAccessKeyError::TooManyAccessKeys {
                    requested_account_id: account_id.clone(),
                    limit: max,
                });
            }
```
