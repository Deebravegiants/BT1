### Title
Storage-usage credit/debit mismatch when access-key/gas-key deletion recomputes storage cost against the *current* `RuntimeFeesConfig` instead of the value used at creation - ([File: runtime/runtime/src/access_keys.rs])

### Summary
`add_regular_key`/`add_gas_key` increment `Account::storage_usage()` by a value computed from the *current* `RuntimeFeesConfig.storage_usage_config` (specifically `num_extra_bytes_record`, plus `public_key.trie_id_len()` and the borsh size of the key) at the moment the key is added. `delete_regular_key`/`delete_gas_key` independently *recompute* the same formula using whatever `RuntimeFeesConfig` is active at the time of deletion and subtract that value, instead of using the amount that was actually added. This is structurally identical to the FrankenDAO `Staking.stake()`/`unstake()` bug: a per-token/per-key "credit" amount is derived from a mutable, admin/protocol-controlled parameter, and the "debit" independently re-derives it from the parameter's *current* value rather than storing and reversing the original credit. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`access_key_storage_usage()` and `gas_key_storage_cost()` both take a `&RuntimeFeesConfig` parameter and use `fee_config.storage_usage_config.num_extra_bytes_record` (a protocol/runtime parameter that is versioned via `RuntimeConfig`/`parameter_table.rs` and can change across protocol-version upgrades) to compute the storage-usage delta charged for an access key or gas key. [1](#0-0) 

- On `AddKey`, `add_regular_key`/`add_gas_key` use `apply_state.config.fees` **at the time of the add** to compute the cost and `checked_add` it to `account.storage_usage()`. [3](#0-2) 
- On `DeleteKey`, `delete_regular_key`/`delete_gas_key` use `config.fees` **at the time of the delete** (i.e., whatever `RuntimeFeesConfig` is active on that block/protocol version) to recompute the same formula and `saturating_sub` it from `account.storage_usage()`. [2](#0-1) 

Nothing stores the originally-added value per key; the delta is derived twice, independently, from the mutable `storage_usage_config`. If a network-wide protocol upgrade changes `num_extra_bytes_record` (or if that field otherwise differs between the add-time config and delete-time config) between when a user adds a key and when they later delete it, the subtracted amount will not equal the amount that was added, exactly as in the reported FrankenDAO issue where `getTokenVotingPower()` used mutable `monsterMultiplier`/`baseVotes` independently at stake and unstake time.

Because the subtraction uses `saturating_sub` rather than a checked subtraction, this cannot panic/revert (unlike the Solidity underflow revert), but it silently corrupts `Account::storage_usage()`:
- If the delete-time cost is *larger* than the add-time cost, the extra amount is subtracted from the account's *other* legitimately-used storage bytes (because `saturating_sub` just floors at zero), permanently under-recording `storage_usage` relative to the account's real trie footprint.
- `storage_usage()` directly feeds `check_storage_stake` (`runtime/runtime/src/verifier.rs:47-83`), which requires `amount + locked >= storage_amount_per_byte * storage_usage()`. An under-recorded `storage_usage` means the account can retain more real trie state (deployed contract, other keys, contract storage) than the tokens it has locked would legitimately back — i.e., underpriced storage. [4](#0-3) 

### Impact Explanation
`storage_usage()` is the accounting field that Storage Staking uses to guarantee "1 NEAR backs ~100KB" globally — every byte of state must be paid for. A persistent under-count of `storage_usage()` (triggered purely by ordinary `AddKey`/`DeleteKey` transactions straddling a protocol-version parameter change) breaks that invariant: an account can end up holding more real state than its locked/available balance is required to cover, which is the "free or underpriced storage" outcome called out as a valid impact class. It does not cause a panic or chain stall (subtraction is saturating), so the severity is bounded to an accounting/economic invariant violation rather than a liveness bug.

### Likelihood Explanation
The reachable trigger is a completely ordinary transaction flow (`AddKey` followed later by `DeleteKey`, or `TransferToGasKey`/gas-key lifecycle) available to any unprivileged account — no validator or node-operator privilege needed. However, the *actual* corruption only manifests if `storage_usage_config.num_extra_bytes_record` (or an input to `access_key_storage_usage`/`gas_key_storage_cost`) genuinely differs between the block where the key was added and the block where it is deleted. I could not confirm from the available index whether this parameter has ever actually changed value across a shipped protocol-version upgrade in `core/parameters/res/runtime_configs/*.yaml`, or whether nearcore's runtime-config versioning mechanism keeps this specific field constant by design; the grep results only located the field, not a version-to-version diff. This uncertainty should be resolved by inspecting the full parameter version history before treating this as confirmed-exploitable today.

### Recommendation
Persist the storage-usage amount that was actually added for a given access key/gas key (e.g., store it alongside the key, or record it in the `AccessKey`/`GasKeyInfo` structure) and subtract that stored value on deletion, rather than recomputing the formula against the delete-time `RuntimeFeesConfig`. This mirrors the FrankenDAO fix's recommendation of caching `tokenVotingPower` at stake time and reversing the exact cached amount at unstake time.

### Proof of Concept
Not independently verified against a real protocol-version parameter change (see Likelihood Explanation) — I was unable to confirm from the indexed files whether `storage_usage_config.num_extra_bytes_record` has changed across any shipped `RuntimeConfig` version in this repo. Conceptually:
1. Account adds an access key at protocol version `Vn`, where `storage_usage_config.num_extra_bytes_record = X`; `storage_usage` increases by `cost(X)` [3](#0-2) .
2. Chain upgrades to protocol version `Vn+1` where `num_extra_bytes_record = Y != X` (hypothetical/future parameter change).
3. Account submits `DeleteKey` for the same key at `Vn+1`; `delete_regular_key`/`delete_gas_key` computes `cost(Y)` and subtracts it via `saturating_sub` [2](#0-1) .
4. If `Y > X`, `account.storage_usage()` decreases by more than it increased, silently consuming "phantom" storage credit from the account's other stored bytes, which then under-collateralizes real state per `check_storage_stake`.

I recommend a Devin/engineering session confirm whether `num_extra_bytes_record` (or any other input to these two cost functions) has ever changed across a protocol version in `core/parameters/res/runtime_configs/`, and if reproducible, add a regression test exercising add/delete across a simulated config change, before treating this as a confirmed live vulnerability.

### Citations

**File:** runtime/runtime/src/access_keys.rs (L17-44)
```rust
fn access_key_storage_usage(
    fee_config: &RuntimeFeesConfig,
    public_key: &PublicKey,
    access_key: &AccessKey,
) -> StorageUsage {
    let storage_usage_config = &fee_config.storage_usage_config;
    // Use the on-trie identifier length, not the borsh-serialized pubkey
    // length: ML-DSA-65 access keys live in the trie as a SHA3-256 hash
    // (33 bytes incl. type tag), not as a 1953-byte full pubkey.
    public_key.trie_id_len() as u64
        + borsh::object_length(access_key).unwrap() as u64
        + storage_usage_config.num_extra_bytes_record
}

fn gas_key_storage_cost(
    fee_config: &RuntimeFeesConfig,
    public_key: &PublicKey,
    access_key: &AccessKey,
    num_nonces: NonceIndex,
) -> StorageUsage {
    let storage_config = &fee_config.storage_usage_config;
    let per_nonce_value_size = borsh::object_length(&(0 as Nonce)).unwrap() as u64;
    let per_nonce_key_size = public_key.trie_id_len() as u64 + size_of::<NonceIndex>() as u64;

    num_nonces as u64
        * (per_nonce_key_size + per_nonce_value_size + storage_config.num_extra_bytes_record)
        + access_key_storage_usage(fee_config, public_key, access_key)
}
```

**File:** runtime/runtime/src/access_keys.rs (L126-147)
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
}
```

**File:** runtime/runtime/src/access_keys.rs (L216-255)
```rust
    account.set_storage_usage(
        account
            .storage_usage()
            .checked_add(gas_key_storage_cost(fee_config, public_key, &access_key, num_nonces))
            .ok_or_else(|| {
                StorageError::StorageInconsistentState(format!(
                    "Storage usage integer overflow for account {}",
                    account_id
                ))
            })?,
    );
    Ok(())
}

fn add_regular_key(
    fee_config: &RuntimeFeesConfig,
    state_update: &mut TrieUpdate,
    account: &mut Account,
    account_id: &AccountId,
    public_key: &PublicKey,
    access_key: &AccessKey,
    block_height: BlockHeight,
) -> Result<(), StorageError> {
    let mut access_key = access_key.clone();
    access_key.nonce = initial_nonce_value(block_height);
    set_access_key(state_update, account_id.clone(), public_key.clone(), &access_key);

    account.set_storage_usage(
        account
            .storage_usage()
            .checked_add(access_key_storage_usage(fee_config, public_key, &access_key))
            .ok_or_else(|| {
                StorageError::StorageInconsistentState(format!(
                    "Storage usage integer overflow for account {}",
                    account_id
                ))
            })?,
    );
    Ok(())
}
```

**File:** runtime/runtime/src/verifier.rs (L47-83)
```rust
pub fn check_storage_stake(
    account: &Account,
    account_balance: Balance,
    runtime_config: &RuntimeConfig,
) -> Result<(), StorageStakingError> {
    let billable_storage_bytes = account.storage_usage();
    let required_amount = runtime_config
        .storage_amount_per_byte()
        .checked_mul(u128::from(billable_storage_bytes))
        .ok_or_else(|| {
            format!(
                "Account's billable storage usage {} overflows multiplication",
                billable_storage_bytes
            )
        })
        .map_err(StorageStakingError::StorageError)?;
    let available_amount = account_balance
        .checked_add(account.locked())
        .ok_or_else(|| {
            format!(
                "Account's amount {} and locked {} overflow addition",
                account.amount(),
                account.locked(),
            )
        })
        .map_err(StorageStakingError::StorageError)?;
    if available_amount >= required_amount {
        Ok(())
    } else {
        if is_zero_balance_account(account) {
            return Ok(());
        }
        Err(StorageStakingError::LackBalanceForStorageStaking(
            required_amount.checked_sub(available_amount).unwrap(),
        ))
    }
}
```
