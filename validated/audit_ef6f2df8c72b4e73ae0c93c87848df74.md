### Title
Missing Ownership Check in `DeployGlobalContractAction` (`AccountId` Mode) Allows Any Account to Overwrite Another Account's Global Contract - (File: `runtime/runtime/src/global_contracts.rs`)

---

### Summary

`DeployGlobalContractAction` with `GlobalContractDeployMode::AccountId` stores a global contract under the **receiver account's** ID as the unique key. Unlike `DeployContract`, `Stake`, `AddKey`, `DeleteKey`, and `DeleteAccount`, there is no enforcement that `predecessor_id == receiver_id` for `DeployGlobalContract`. Any unprivileged account can therefore send a `DeployGlobalContract(AccountId, malicious_code)` receipt to any victim account, overwriting the victim's global contract with attacker-controlled code, draining the victim's balance for storage costs, and corrupting the runtime state for every account that references the victim's global contract identifier.

---

### Finding Description

`GlobalContractDeployMode::AccountId` is documented as allowing **the owner** to update the contract for all its users:

```rust
/// Contract is deployed under the owner account id.
/// Users will be able reference it by that account id.
/// This allows the owner to update the contract for all its users.
AccountId,
``` [1](#0-0) 

In `action_deploy_global_contract`, the identifier used to store the contract in the trie is derived from `account_id`, which is the **receipt receiver**, not the sender:

```rust
GlobalContractDeployMode::AccountId => {
    GlobalContractIdentifier::AccountId(account_id.clone())
}
``` [2](#0-1) 

The storage cost is then deducted from the **receiver's** account balance:

```rust
let Some(updated_balance) = account.amount().checked_sub(storage_cost) else { ... };
account.set_amount(updated_balance);
``` [3](#0-2) 

The only validation performed on `DeployGlobalContractAction` is a size check — no ownership or sender-receiver equality check exists:

```rust
fn validate_deploy_global_contract_action(
    limit_config: &LimitConfig,
    action: &DeployGlobalContractAction,
) -> Result<(), ActionsValidationError> {
    if action.code.len() as u64 > limit_config.max_contract_size {
        return Err(ActionsValidationError::ContractSizeExceeded { ... });
    }
    Ok(())
}
``` [4](#0-3) 

The NEAR protocol explicitly lists the actions that require `predecessor_id == receiver_id`: `DeployContract`, `Stake`, `AddKey`, `DeleteKey`, `DeleteAccount`. `DeployGlobalContract` is **absent** from this list, confirming it can be directed at any account. The `check_account_existence` function for `DeployGlobalContract` only verifies the receiver account exists: [5](#0-4) 

The distribution receipt is then propagated to all shards, writing the attacker's code to `TrieKey::GlobalContractCode { identifier: GlobalContractCodeIdentifier::AccountId(victim) }` on every shard: [6](#0-5) 

---

### Impact Explanation

An attacker who sends a transaction with `receiver_id = victim` and action `DeployGlobalContract { code: malicious_wasm, deploy_mode: AccountId }` achieves:

1. **Global contract state corruption**: `TrieKey::GlobalContractCode { identifier: AccountId(victim) }` is overwritten with attacker-controlled WebAssembly on every shard.
2. **Balance drain**: The storage cost (`global_contract_storage_amount_per_byte * code.len()`) is deducted from the victim's account, not the attacker's.
3. **All downstream users compromised**: Every account that has called `UseGlobalContract(AccountId(victim))` now executes the malicious contract on any subsequent function call, because `AccountContract::GlobalByAccount(victim)` points to the overwritten code.

The corrupted trie value is the concrete protocol state that is damaged: `TrieKey::GlobalContractCode` for the victim's account ID, replicated across all shards via `GlobalContractDistributionReceipt`. [7](#0-6) 

---

### Likelihood Explanation

The attack requires only a valid NEAR account with enough NEAR to pay gas fees. The attacker does not need any special privileges. The victim's account must exist and have sufficient balance to cover the storage cost; accounts that deploy global contracts are by definition funded. The attack is a single signed transaction submitted via public RPC, directly analogous to the `enrollCourier` front-run: the attacker simply targets the victim's account ID as the receiver.

---

### Recommendation

Add an ownership check in `action_deploy_global_contract` (or in `validate_deploy_global_contract_action` / the broader action validation pipeline) that, when `deploy_mode == AccountId`, requires `predecessor_id == receiver_id`. This mirrors the existing restriction on `DeployContract`, `Stake`, `AddKey`, `DeleteKey`, and `DeleteAccount`. Alternatively, add `DeployGlobalContract` to the set of actions that enforce `ActorNoPermission` when `predecessor_id != receiver_id`. [8](#0-7) 

---

### Proof of Concept

```
1. Attacker (account: "attacker.near") constructs a SignedTransaction:
     signer_id    = "attacker.near"
     receiver_id  = "victim.near"          // victim who owns a global contract
     actions      = [DeployGlobalContract {
                       code: <malicious_wasm>,
                       deploy_mode: AccountId,
                     }]

2. Transaction is submitted via public RPC (broadcast_tx_commit).

3. Runtime executes action_deploy_global_contract on "victim.near":
     - storage_cost deducted from victim.near's balance
     - initiate_distribution called with account_id = "victim.near"
     - identifier = GlobalContractIdentifier::AccountId("victim.near")
     - nonce incremented for this identifier

4. GlobalContractDistributionReceipt propagates to all shards.
   apply_distribution_current_shard writes:
     TrieKey::GlobalContractCode { identifier: AccountId("victim.near") }
     = <malicious_wasm>
   on every shard (nonce check passes because attacker's nonce > any prior nonce).

5. All accounts that previously called UseGlobalContract(AccountId("victim.near"))
   now execute <malicious_wasm> on their next function call.
``` [9](#0-8) [10](#0-9)

### Citations

**File:** core/primitives/src/action/mod.rs (L133-142)
```rust
pub enum GlobalContractDeployMode {
    /// Contract is deployed under its code hash.
    /// Users will be able reference it by that hash.
    /// This effectively makes the contract immutable.
    CodeHash,
    /// Contract is deployed under the owner account id.
    /// Users will be able reference it by that account id.
    /// This allows the owner to update the contract for all its users.
    AccountId,
}
```

**File:** runtime/runtime/src/global_contracts.rs (L23-61)
```rust
pub(crate) fn action_deploy_global_contract(
    state_update: &mut TrieUpdate,
    account: &mut Account,
    account_id: &AccountId,
    apply_state: &ApplyState,
    deploy_contract: &DeployGlobalContractAction,
    result: &mut ActionResult,
) -> Result<(), RuntimeError> {
    let _span = tracing::debug_span!(target: "runtime", "action_deploy_global_contract").entered();

    let storage_cost = apply_state
        .config
        .fees
        .storage_usage_config
        .global_contract_storage_amount_per_byte
        .saturating_mul(deploy_contract.code.len() as u128);
    let Some(updated_balance) = account.amount().checked_sub(storage_cost) else {
        result.result = Err(ActionErrorKind::LackBalanceForState {
            account_id: account_id.clone(),
            amount: storage_cost,
        }
        .into());
        return Ok(());
    };
    result.tokens_burnt =
        result.tokens_burnt.checked_add(storage_cost).ok_or(IntegerOverflowError)?;
    account.set_amount(updated_balance);

    initiate_distribution(
        state_update,
        account_id.clone(),
        deploy_contract.code.clone(),
        &deploy_contract.deploy_mode,
        apply_state.shard_id,
        result,
    )?;

    Ok(())
}
```

**File:** runtime/runtime/src/global_contracts.rs (L63-107)
```rust
pub(crate) fn action_use_global_contract(
    state_update: &mut TrieUpdate,
    account_id: &AccountId,
    account: &mut Account,
    action: &UseGlobalContractAction,
    result: &mut ActionResult,
) -> Result<(), RuntimeError> {
    let _span = tracing::debug_span!(target: "runtime", "action_use_global_contract").entered();
    use_global_contract(state_update, account_id, account, &action.contract_identifier, result)
}

pub(crate) fn use_global_contract(
    state_update: &mut TrieUpdate,
    account_id: &AccountId,
    account: &mut Account,
    contract_identifier: &GlobalContractIdentifier,
    result: &mut ActionResult,
) -> Result<(), RuntimeError> {
    let key = TrieKey::GlobalContractCode { identifier: contract_identifier.clone().into() };
    if !state_update.contains_key(&key, AccessOptions::DEFAULT)? {
        result.result = Err(ActionErrorKind::GlobalContractDoesNotExist {
            identifier: contract_identifier.clone(),
        }
        .into());
        return Ok(());
    }
    clear_account_contract_storage_usage(state_update, account_id, account)?;
    if account.contract().is_local() {
        state_update.remove(TrieKey::ContractCode { account_id: account_id.clone() });
    }
    let contract = match contract_identifier {
        GlobalContractIdentifier::CodeHash(code_hash) => AccountContract::Global(*code_hash),
        GlobalContractIdentifier::AccountId(id) => AccountContract::GlobalByAccount(id.clone()),
    };
    account.set_storage_usage(
        account.storage_usage().checked_add(contract_identifier.len() as u64).ok_or_else(|| {
            StorageError::StorageInconsistentState(format!(
                "Storage usage integer overflow for account {}",
                account_id
            ))
        })?,
    );
    account.set_contract(contract);
    Ok(())
}
```

**File:** runtime/runtime/src/global_contracts.rs (L141-169)
```rust
fn initiate_distribution(
    state_update: &mut TrieUpdate,
    account_id: AccountId,
    contract_code: Arc<[u8]>,
    deploy_mode: &GlobalContractDeployMode,
    current_shard_id: ShardId,
    result: &mut ActionResult,
) -> Result<(), RuntimeError> {
    let id = match deploy_mode {
        GlobalContractDeployMode::CodeHash => {
            GlobalContractIdentifier::CodeHash(hash(&contract_code))
        }
        GlobalContractDeployMode::AccountId => {
            GlobalContractIdentifier::AccountId(account_id.clone())
        }
    };
    // Increment the nonce and write it to state immediately to prevent multiple
    // distributions with the same nonce from being initiated. This requires
    // allowing the same nonce in the freshness check when applying the
    // distribution receipt.
    let nonce = increment_nonce(state_update, &id)?;
    let distribution_receipt =
        GlobalContractDistributionReceipt::new(id, current_shard_id, vec![], contract_code, nonce);
    let distribution_receipts =
        Receipt::new_global_contract_distribution(account_id, distribution_receipt);
    // No need to set receipt_id here, it will be generated as part of apply_action_receipt
    result.new_receipts.push(distribution_receipts);
    Ok(())
}
```

**File:** runtime/runtime/src/global_contracts.rs (L189-233)
```rust
fn apply_distribution_current_shard(
    receipt: &Receipt,
    global_contract_data: &GlobalContractDistributionReceipt,
    apply_state: &ApplyState,
    state_update: &mut TrieUpdate,
) -> Result<Compute, RuntimeError> {
    let identifier = match &global_contract_data.id() {
        GlobalContractIdentifier::CodeHash(hash) => GlobalContractCodeIdentifier::CodeHash(*hash),
        GlobalContractIdentifier::AccountId(account_id) => {
            GlobalContractCodeIdentifier::AccountId(account_id.clone())
        }
    };

    let is_nonce_fresh = check_and_update_nonce(global_contract_data, &identifier, state_update)?;
    if !is_nonce_fresh {
        return Ok(0);
    }

    let config = apply_state.config.wasm_config.clone();
    let trie_key = TrieKey::GlobalContractCode { identifier };
    let code_len = global_contract_data.code().len() as u64;
    state_update.set(trie_key, global_contract_data.code().to_vec());
    state_update.commit(StateChangeCause::ReceiptProcessing { receipt_hash: receipt.get_hash() });
    let code_hash = match global_contract_data.id() {
        GlobalContractIdentifier::CodeHash(hash) => Some(*hash),
        GlobalContractIdentifier::AccountId(_) => None,
    };
    precompile_contract_with_warming(
        &ContractCode::new(global_contract_data.code().to_vec(), code_hash),
        config,
        apply_state.next_wasm_config.clone(),
        apply_state.cache.as_deref(),
    );
    near_vm_runner::report_metrics(apply_state.shard_id, "global_contract");
    let fees = &apply_state.config.fees;
    let per_byte_total = fees
        .deploy_global_contract_execution_per_byte
        .checked_mul(code_len)
        .ok_or(IntegerOverflowError)?;
    let compute = fees
        .deploy_global_contract_execution_base
        .checked_add(per_byte_total)
        .ok_or(IntegerOverflowError)?;
    Ok(compute)
}
```

**File:** runtime/runtime/src/action_validation.rs (L225-238)
```rust
/// Validates `DeployGlobalContractAction`. Checks that the given contract size doesn't exceed the limit.
fn validate_deploy_global_contract_action(
    limit_config: &LimitConfig,
    action: &DeployGlobalContractAction,
) -> Result<(), ActionsValidationError> {
    if action.code.len() as u64 > limit_config.max_contract_size {
        return Err(ActionsValidationError::ContractSizeExceeded {
            size: action.code.len() as u64,
            limit: limit_config.max_contract_size,
        });
    }

    Ok(())
}
```

**File:** runtime/runtime/src/actions.rs (L806-824)
```rust
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
```
