## Title
Global Contract "Owner" Can Silently Rug-Pull Any Account That References It in `AccountId` Mode - (File: `runtime/runtime/src/global_contracts.rs`)

## Summary
NEAR's global-contract feature (`DeployGlobalContractAction` / `UseGlobalContractAction`) contains the exact centralization pattern flagged in the Blur `ExecutionDelegate` report: a single privileged account (the global-contract "owner") can unilaterally replace the WASM logic that runs *with full custody of another account's balance and storage*, at any time, with no on-chain consent step from the referencing account and no way for that account to "revoke" trust before the next call executes the new code.

## Finding Description
`GlobalContractDeployMode::AccountId` is explicitly documented as giving the deployer permanent update rights over any account that adopts it: "Contract is deployed under the owner account id. Users will be able reference it by that account id. This allows the owner to update the contract for all its users." [1](#0-0)  This is echoed in the runtime spec docs. [2](#0-1) 

A user account opts in once via `UseGlobalContractAction`, which stores a mutable pointer (`AccountContract::GlobalByAccount(id)`) rather than a pinned code hash: [3](#0-2) 

From that point on, every function call against the referencing account resolves its executable code dynamically through this pointer: [4](#0-3) 

The deployer/"owner" can redeploy new code under that same `AccountId` identifier at any time using `action_deploy_global_contract`, which simply re-initiates distribution of new bytes under the same identifier — there is no re-approval, timelock, or notification to accounts that already reference it: [5](#0-4)  The nonce mechanism (`increment_nonce` / `check_and_update_nonce`) only exists to guarantee monotonic/idempotent propagation of updates across shards — it is not a consent or freshness-pinning mechanism for the referencing account. [6](#0-5) 

This is functionally identical to the Blur bug class: users "approve" a delegate (here, `UseGlobalContract` in `AccountId` mode) that a privileged owner can redirect/rewrite at will, and there is no timing-safe way for the trusting account to "revoke" before the owner's next update takes effect on their own account — the referencing account has no lock-in protection analogous to a pinned `CodeHash` unless it explicitly chooses that separate, immutable mode from the start.

## Impact Explanation
Once an account executes `UseGlobalContract` with `GlobalContractIdentifier::AccountId`, the referenced-contract owner effectively gains full remote-code-execution control over that account: subsequent WASM logic runs with the account's own permissions, meaning it can issue `Transfer`, `AddKey`/`DeleteKey`, or further contract-calling actions that move the account's NEAR balance or drain its storage — all under the guise of code the account never re-approved. Test infrastructure such as `test_global_contract_update` confirms that a redeploy under `AccountId` mode immediately changes behavior for every account still referencing that identifier. [7](#0-6)  An owner (or an attacker who compromises the owner's key) can push malicious logic that transfers out the balance of every dependent account — concrete unauthorized balance/state change and theft, reachable purely through standard transactions (`DeployGlobalContractAction`, `UseGlobalContractAction`) with no validator or node-level privilege required.

## Likelihood Explanation
This requires no protocol bug exploitation — it is reachable via ordinary transactions available to any account: a malicious or compromised global-contract owner deploys under `AccountId` mode, waits for other accounts to opt in via `UseGlobalContract`, then redeploys hostile code. The likelihood scales with adoption of shared `AccountId`-mode global contracts (which is precisely the incentive for using this mode, e.g., to reduce per-account storage as shown in the ZBA test). [8](#0-7) 

## Recommendation
- Document prominently (beyond the current one-line comment) that `AccountId`-mode global contracts constitute full custodial trust in the deployer, equivalent to giving away a full-access key.
- Offer referencing accounts a way to "pin" the currently-referenced code (e.g., record the code hash active at time of `UseGlobalContract` and require an explicit re-approval action to move to a newer hash under the same `AccountId`), rather than always resolving to whatever the owner has most recently pushed.
- Consider a timelock/delay on `AccountId`-mode redeployments and/or an event/expiry mechanism so dependent accounts have a window to detect and opt out (switch to `CodeHash` mode or remove the contract) before a malicious update takes effect on their own account.

## Proof of Concept
1. Attacker (or legitimate owner later compromised/turned malicious) submits `DeployGlobalContractAction { deploy_mode: AccountId }` deploying benign code under `owner.near`.
2. Victim account calls `UseGlobalContractAction { contract_identifier: AccountId(owner.near) }`, adopting the code — analogous to a Blur user approving `ExecutionDelegate`. [9](#0-8) 
3. Owner later submits a new `DeployGlobalContractAction` under the same `AccountId` identifier containing code that, when called, issues `Transfer` actions draining the victim account's balance to an attacker-controlled address.
4. Any subsequent function call to the victim account resolves to the new malicious code via `RuntimeContractIdentifier::resolve` and executes with the victim's full account authority — no additional consent, signature, or notice from the victim was required for this state/balance change. [10](#0-9)

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

**File:** docs/RuntimeSpec/Actions.md (L440-450)
```markdown
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
```

**File:** runtime/runtime/src/global_contracts.rs (L24-62)
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

**File:** runtime/runtime/src/global_contracts.rs (L75-107)
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
    account.set_contract(contract).or_inconsistent_state(account_id)?;
    Ok(())
```

**File:** runtime/runtime/src/global_contracts.rs (L142-188)
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

/// Increments the nonce for the given global contract identifier and writes
/// it to state immediately.
fn increment_nonce(
    state_update: &mut TrieUpdate,
    id: &GlobalContractIdentifier,
) -> Result<u64, RuntimeError> {
    let identifier: GlobalContractCodeIdentifier = id.clone().into();

    let nonce_key = TrieKey::GlobalContractNonce { identifier };
    let stored_nonce = get_nonce(state_update, &nonce_key)?;

    let new_nonce = stored_nonce.checked_add(1).ok_or_else(|| {
        RuntimeError::UnexpectedIntegerOverflow("increment_global_contract_nonce".into())
    })?;
    set_nonce(state_update, nonce_key, new_nonce);
    Ok(new_nonce)
}
```

**File:** runtime/runtime/src/contract_code.rs (L36-50)
```rust
    pub(crate) fn resolve(
        account_id: &AccountId,
        account_contract: AccountContract,
        state_update: &TrieUpdate,
        chain_id: &str,
        access: AccessOptions,
    ) -> Result<Self, StorageError> {
        let local_hash = match GlobalContractIdentifier::try_from(account_contract) {
            Ok(gci) => {
                let code_hash = gci.clone().hash(state_update, access)?;
                return Ok(RuntimeContractIdentifier::Global { code_hash, identifier: gci });
            }
            Err(ContractIsLocalError::NotDeployed) => return Ok(RuntimeContractIdentifier::None),
            Err(ContractIsLocalError::Deployed(local_hash)) => local_hash,
        };
```

**File:** test-loop-tests/src/tests/global_contracts.rs (L71-106)
```rust
#[test]
fn test_global_contract_update() {
    let mut env = GlobalContractsTestEnv::setup(Balance::from_near(1000));
    let use_accounts = [env.account_shard_0.clone(), env.account_shard_1.clone()];

    env.deploy_trivial_global_contract(GlobalContractDeployMode::AccountId);

    for account in &use_accounts {
        env.use_global_contract(
            account,
            GlobalContractIdentifier::AccountId(env.deploy_account.clone()),
        );

        // Currently deployed trivial contract doesn't have any methods,
        // so we expect any function call to fail with MethodNotFound error
        let call_tx = env.call_global_contract_tx(account.clone(), account.clone());
        let call_outcome = env.execute_tx(call_tx);
        assert_matches!(
            call_outcome.status,
            FinalExecutionStatus::Failure(TxExecutionError::ActionError(ActionError {
                kind: ActionErrorKind::FunctionCallError(FunctionCallError::MethodResolveError(
                    MethodResolveError::MethodNotFound
                )),
                index: _
            }))
        );
    }

    env.deploy_global_contract(GlobalContractDeployMode::AccountId);

    for account in &use_accounts {
        // Function call should be successful after deploying rs contract
        // containing the function we call here
        env.assert_call_global_contract_success(account.clone(), account.clone());
    }
}
```

**File:** integration-tests/src/tests/runtime/test_yield_resume.rs (L638-661)
```rust
// The 1-yoctoNEAR exemption in VMLogic only fires when `current_account_balance`
// is exactly zero. To reach that state end-to-end the contract must drain its
// entire balance via a Transfer promise in the same wasm call. The runtime's
// `check_storage_stake` would normally reject a contract account with 0 balance,
// but Zero Balance Accounts (NEP-448) — accounts whose `storage_usage` fits
// within `ZERO_BALANCE_ACCOUNT_STORAGE_LIMIT` (770 bytes) — are exempt from
// that check (see `verifier.rs::check_storage_stake`).
//
// The standard `rs_contract` is large (~100 KB), so it can't be a ZBA. To get
// the test contract API on a ZBA, we deploy it once as a *global* contract from
// `alice.near` and have a small account (`zba.alice.near`) reference it via
// `UseGlobalContract` — that leaves the referencing account at ~150 bytes of
// storage, well within the ZBA limit.
fn setup_zba_global_contract() -> (RuntimeNode, AccountId) {
    use testlib::runtime_utils::alice_account;
    let node = RuntimeNode::new(&alice_account());
    let alice_id = alice_account();
    let zba_id: AccountId = "zba.alice.near".parse().unwrap();

    // Deploy rs_contract as a global contract owned by alice.near.
    let deploy = vec![Action::DeployGlobalContract(DeployGlobalContractAction {
        code: near_test_contracts::rs_contract().to_vec().into(),
        deploy_mode: GlobalContractDeployMode::AccountId,
    })];
```

**File:** core/primitives/src/test_utils.rs (L343-362)
```rust
    pub fn use_global_contract(
        nonce: Nonce,
        account_id: &AccountId,
        signer: &Signer,
        block_hash: CryptoHash,
        contract_identifier: GlobalContractIdentifier,
    ) -> SignedTransaction {
        let signer_id = account_id.clone();
        let receiver_id = account_id.clone();
        SignedTransaction::from_actions(
            nonce,
            signer_id,
            receiver_id,
            &signer,
            vec![Action::UseGlobalContract(Box::new(UseGlobalContractAction {
                contract_identifier,
            }))],
            block_hash,
        )
    }
```
