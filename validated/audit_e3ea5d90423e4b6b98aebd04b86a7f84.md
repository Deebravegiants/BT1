### Title
Global Contract Owner Can Silently Replace WASM Code for All Subscriber Accounts Without Timelock or Consent - (File: runtime/runtime/src/global_contracts.rs)

### Summary
The `GlobalContractDeployMode::AccountId` feature grants a global contract deployer unilateral, unconstrained power to replace the WASM code executing on every account that has opted in via `UseGlobalContract`. There is no timelock, no subscriber consent mechanism, and no opt-out path. A deployer who initially publishes a legitimate contract can later push malicious code that drains subscriber balances or installs backdoor keys — a direct runtime-state analog to the `setHandler` excessive-permissions class.

### Finding Description
When an account calls `DeployGlobalContractAction` with `deploy_mode = GlobalContractDeployMode::AccountId`, the runtime stores the WASM blob under `TrieKey::GlobalContractCode { identifier: GlobalContractCodeIdentifier::AccountId(deployer_id) }` and initiates cross-shard distribution via `initiate_distribution`.

Any account that subsequently calls `UseGlobalContractAction` with `GlobalContractIdentifier::AccountId(deployer_id)` has its trie `AccountContract` field set to `AccountContract::GlobalByAccount(deployer_id)`. From that point on, every function call on that account executes whatever WASM blob is currently stored under the deployer's key — not the blob that was present when the subscriber opted in.

The deployer can call `DeployGlobalContractAction` again at any time. `action_deploy_global_contract` (lines 23–61 of `global_contracts.rs`) performs no access control beyond the `check_actor_permissions` guard that only verifies `actor_id == account_id` (i.e., the deployer is the transaction signer). There is no timelock, no subscriber notification, and no mechanism for subscribers to freeze their contract version.

The `check_and_update_nonce` function (lines 238–256) only prevents a *stale* distribution receipt from overwriting a *newer* one during cross-shard propagation. It does not prevent the owner from issuing a fresh, higher-nonce update with arbitrary new code. Once the new `GlobalContractDistributionReceipt` propagates to all shards via `apply_distribution_current_shard` (line 210: `state_update.set(trie_key, global_contract_data.code().to_vec())`), every subscriber account silently executes the replacement code.

The design intent is documented explicitly in `core/primitives/src/action/mod.rs` line 140: *"This allows the owner to update the contract for all its users."* No protocol-level guard limits what the replacement code may do.

### Impact Explanation
After a malicious update propagates, the replacement WASM executes with full host-function access on each subscriber account. Concrete effects:

- **Balance theft**: the contract calls `promise_batch_action_transfer` to move the subscriber's entire balance to the attacker.
- **Key injection**: the contract calls `promise_batch_action_add_key` with a full-access key controlled by the attacker, permanently backdooring the account.
- **Account deletion**: the contract calls `promise_batch_action_delete_account` with the attacker as beneficiary.

The corrupted protocol values are the subscriber accounts' `AccountContract` trie entries (changed from a trusted to a malicious code pointer) and the resulting `amount` balance fields after the malicious receipts execute. These are concrete, on-chain state-root changes.

### Likelihood Explanation
The global contract feature is explicitly designed for shared libraries and token standards — high-value targets where many accounts opt in to a single deployer. A deployer who builds reputation with a legitimate contract and accumulates subscribers can execute the rug-pull with a single signed transaction. No validator collusion, no node access, and no special privilege beyond owning the deployer account is required. The attack is atomic from the deployer's perspective: one `DeployGlobalContractAction` transaction triggers distribution to all shards.

### Recommendation
Mirror the partial fix applied in the original report: introduce a protocol-enforced timelock on `AccountId`-mode global contract updates. Concretely, record a `pending_update_at_block` in the trie when a new deployment is initiated and reject distribution receipts whose originating block is within the timelock window. Alternatively, allow subscriber accounts to pin a specific nonce (code version) so they are not silently upgraded.

### Proof of Concept
1. **Setup**: Attacker (`evil.near`) deploys a benign global contract via a signed `DeployGlobalContractAction { deploy_mode: AccountId }` transaction. Cost: storage fee only.
2. **Subscription**: Victim accounts call `UseGlobalContractAction { contract_identifier: AccountId("evil.near") }`. Their `AccountContract` is now `GlobalByAccount("evil.near")`.
3. **Attack**: Attacker sends a second `DeployGlobalContractAction` with malicious WASM. `action_deploy_global_contract` (lines 23–61, `global_contracts.rs`) accepts it unconditionally, increments the nonce, and enqueues a `GlobalContractDistributionReceipt`.
4. **Propagation**: `apply_distribution_current_shard` (line 210) overwrites `TrieKey::GlobalContractCode { identifier: AccountId("evil.near") }` on every shard with the malicious blob.
5. **Execution**: The next function call on any victim account executes the malicious WASM, which issues a `Transfer` promise draining the victim's balance to the attacker. The victim's `amount` field in the trie is set to zero; the attacker's balance increases by the same amount.

The root cause is the absence of any update-rate or consent control in `action_deploy_global_contract` and `initiate_distribution` in `runtime/runtime/src/global_contracts.rs`.

---

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** core/primitives/src/action/mod.rs (L133-141)
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

**File:** runtime/runtime/src/global_contracts.rs (L74-107)
```rust
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

**File:** runtime/runtime/src/global_contracts.rs (L238-256)
```rust
fn check_and_update_nonce(
    global_contract_data: &GlobalContractDistributionReceipt,
    identifier: &GlobalContractCodeIdentifier,
    state_update: &mut TrieUpdate,
) -> Result<bool, RuntimeError> {
    let nonce_key = TrieKey::GlobalContractNonce { identifier: identifier.clone() };
    let stored_nonce = get_nonce(state_update, &nonce_key)?;
    let incoming_nonce = global_contract_data.nonce();

    // Allow the same nonce since the nonce is updated immediately when
    // initiating distribution to prevent multiple distributions with the same
    // nonce from being initiated.
    if incoming_nonce < stored_nonce {
        return Ok(false);
    }

    set_nonce(state_update, nonce_key, incoming_nonce);
    Ok(true)
}
```

**File:** runtime/runtime/src/actions.rs (L717-732)
```rust
    match action {
        Action::DeployContract(_)
        | Action::Stake(_)
        | Action::AddKey(_)
        | Action::DeleteKey(_)
        | Action::DeployGlobalContract(_)
        | Action::UseGlobalContract(_)
        | Action::WithdrawFromGasKey(_) => {
            if actor_id != account_id {
                return Err(ActionErrorKind::ActorNoPermission {
                    account_id: account_id.clone(),
                    actor_id: actor_id.clone(),
                }
                .into());
            }
        }
```
