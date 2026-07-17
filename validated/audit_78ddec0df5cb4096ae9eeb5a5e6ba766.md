### Title
Unprivileged Cross-Contract Overwrite of `GlobalContractDeployMode::AccountId` Global Contract - (File: `runtime/runtime/src/global_contracts.rs`)

### Summary
`action_deploy_global_contract` contains no access-control check verifying that the receipt's predecessor is the account that owns the global contract slot. Any unprivileged user can deploy a malicious contract, create a cross-contract promise targeting a victim account, and append a `DeployGlobalContractAction` with `GlobalContractDeployMode::AccountId`. When the receipt executes on the victim account, the runtime overwrites the global contract stored under the victim's account ID in the trie, replacing the code executed by every account that references it via `GlobalContractIdentifier::AccountId(victim)`.

### Finding Description

`GlobalContractDeployMode::AccountId` is explicitly documented as an owner-controlled upgrade mechanism:

> "Contract is deployed under the owner account id. This allows the **owner** to update the contract for all its users." [1](#0-0) 

The execution path for this action is `action_deploy_global_contract` → `initiate_distribution`. Neither function checks that the receipt's predecessor equals the account whose slot is being written: [2](#0-1) 

The only guard is a balance check (storage cost). `initiate_distribution` blindly uses `account_id` (the receipt receiver) as the `GlobalContractIdentifier::AccountId` key: [3](#0-2) 

The static validation function `validate_deploy_global_contract_action` only checks contract size: [4](#0-3) 

The host function `promise_batch_action_deploy_global_contract_by_account_id` allows any executing contract to append this action to a promise targeting **any** account, with no restriction: [5](#0-4) 

### Impact Explanation

An attacker overwrites `TrieKey::GlobalContractCode { identifier: GlobalContractCodeIdentifier::AccountId(victim_account) }` in the state trie. Every account that has called `UseGlobalContractAction` referencing `GlobalContractIdentifier::AccountId(victim_account)` stores `AccountContract::GlobalByAccount(victim_account)` and will now execute the attacker's injected code on every subsequent function call. This is a direct runtime state corruption: the contract code executed for all users of the global contract is replaced without the owner's consent. [6](#0-5) 

### Likelihood Explanation

Any account with a deployed contract can trigger this. The attacker pays only gas and the storage cost for the victim account (which may already be funded). No validator, node-admin, or trusted-service privilege is required. The attack is a single signed transaction from an unprivileged account.

### Recommendation

In `action_deploy_global_contract`, when `deploy_mode == GlobalContractDeployMode::AccountId`, verify that `receipt.predecessor_id() == account_id` (i.e., the action is self-initiated). Cross-contract calls targeting another account must not be permitted to overwrite that account's named global contract slot.

### Proof of Concept

```
// Attacker deploys this contract to attacker.near
pub fn overwrite_victim_global_contract() {
    // Create a cross-contract promise targeting victim.near
    let promise = env::promise_batch_create("victim.near");
    // Append DeployGlobalContractAction (AccountId mode) with malicious code
    env::promise_batch_action_deploy_global_contract_by_account_id(
        promise,
        MALICIOUS_WASM_CODE,
    );
}
// After execution:
// TrieKey::GlobalContractCode { AccountId("victim.near") } = MALICIOUS_WASM_CODE
// All accounts using GlobalContractIdentifier::AccountId("victim.near") now run attacker code
```

The attacker calls `overwrite_victim_global_contract()` on their own contract. The resulting receipt executes `action_deploy_global_contract` on `victim.near` with no predecessor check, increments the nonce, and initiates distribution of the malicious code to all shards via `initiate_distribution`. [7](#0-6)

### Citations

**File:** core/primitives/src/action/mod.rs (L138-141)
```rust
    /// Contract is deployed under the owner account id.
    /// Users will be able reference it by that account id.
    /// This allows the owner to update the contract for all its users.
    AccountId,
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

**File:** runtime/runtime/src/global_contracts.rs (L141-168)
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
```

**File:** runtime/runtime/src/global_contracts.rs (L189-211)
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
```

**File:** runtime/runtime/src/action_validation.rs (L226-238)
```rust
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

**File:** runtime/near-vm-runner/src/logic/logic.rs (L2558-2599)
```rust
    pub fn promise_batch_action_deploy_global_contract_by_account_id(
        &mut self,
        promise_idx: u64,
        code_len: u64,
        code_ptr: u64,
    ) -> Result<()> {
        self.promise_batch_action_deploy_global_contract_impl(
            promise_idx,
            code_len,
            code_ptr,
            GlobalContractDeployMode::AccountId,
            "promise_batch_action_deploy_global_contract_by_account_id",
        )
    }

    fn promise_batch_action_deploy_global_contract_impl(
        &mut self,
        promise_idx: u64,
        code_len: u64,
        code_ptr: u64,
        mode: GlobalContractDeployMode,
        method_name: &str,
    ) -> Result<()> {
        self.result_state.gas_counter.pay_base(base)?;
        if self.context.is_view() {
            return Err(HostError::ProhibitedInView { method_name: method_name.to_owned() }.into());
        }
        let code = get_memory_or_register!(self, code_ptr, code_len)?;
        let code_len = code.len() as u64;
        let limit = self.config.limit_config.max_contract_size;
        if code_len > limit {
            return Err(HostError::ContractSizeExceeded { size: code_len, limit }.into());
        }
        let code = code.into_owned();

        let (receipt_idx, sir) = self.promise_idx_to_receipt_idx_with_sir(promise_idx)?;

        self.pay_action_base(ActionCosts::deploy_global_contract_base, sir)?;
        self.pay_action_per_byte(ActionCosts::deploy_global_contract_byte, code_len, sir)?;

        self.ext.append_action_deploy_global_contract(receipt_idx, code, mode);
        Ok(())
```
