### Title
Mutable `GlobalContractIdentifier::AccountId` Reference Allows Deployer to Execute Arbitrary Code in Any User Account - (`runtime/runtime/src/global_contracts.rs`)

### Summary

When an account opts into a global contract using `UseGlobalContractAction` with `GlobalContractIdentifier::AccountId(deployer)`, its contract field is permanently bound to the deployer's AccountId key. Because `DeployGlobalContractAction` with `AccountId` mode unconditionally overwrites the code stored at that key, the deployer can silently replace the code executed in every user account that referenced them — without any consent or notification mechanism. The next function call to any such user account executes the deployer's new (potentially malicious) code in the user's own account context, enabling full account takeover or balance drain.

### Finding Description

NEAR's global contract system supports two identifier modes:

- `GlobalContractIdentifier::CodeHash(hash)` — immutable; the code hash is fixed at use-time.
- `GlobalContractIdentifier::AccountId(deployer)` — mutable; the code is resolved at call-time from whatever is currently stored under the deployer's AccountId key.

When Bob calls `UseGlobalContractAction` with `GlobalContractIdentifier::AccountId(alice)`, `action_use_global_contract` stores `AccountContract::GlobalByAccount(alice)` in Bob's account state: [1](#0-0) 

Later, when any function call targets Bob's account, `RuntimeContractIdentifier::resolve()` is called with Bob's `AccountContract::GlobalByAccount(alice)`. It converts this to `GlobalContractIdentifier::AccountId(alice)` and calls `.hash()` on it, which performs a live trie lookup of `TrieKey::GlobalContractCode { identifier: GlobalContractCodeIdentifier::AccountId(alice) }` to get the **current** code hash: [2](#0-1) [3](#0-2) 

Meanwhile, Alice can redeploy a new global contract under her AccountId at any time. `apply_distribution_current_shard` unconditionally overwrites the stored code at that trie key: [4](#0-3) 

There is no version gate, no consent check, and no mechanism for Bob to lock the code hash he originally opted into. The `test_global_contract_update` test explicitly confirms this behavior is reachable: after the deployer redeploys, all user accounts immediately execute the new code: [5](#0-4) 

The function call dispatch in `lib.rs` resolves the contract at execution time, not at `UseGlobalContractAction` time: [6](#0-5) 

### Impact Explanation

The malicious code runs in Bob's account context. NEAR's WASM host functions allow the executing code to:

- Issue `promise_batch_action_transfer` to drain Bob's entire NEAR balance to Alice's account.
- Issue `promise_batch_action_add_key` to add Alice's full-access key to Bob's account, achieving permanent account takeover.
- Corrupt or wipe Bob's contract storage.

The corrupted protocol values are: Bob's `amount` balance (drained), Bob's access key set (new key added), and Bob's contract storage (arbitrary writes). These are committed to the state trie and finalized on-chain.

### Likelihood Explanation

Any unprivileged account can deploy a global contract. The `AccountId` mode is explicitly documented and supported. A malicious actor can advertise a useful contract (e.g., a DeFi primitive, a token standard), attract many accounts to use it via `UseGlobalContractAction`, and then redeploy malicious code. The attack requires only two standard signed transactions (deploy + redeploy) and is triggered automatically on the next function call to any victim account. No validator or node-admin privilege is required.

### Recommendation

1. **Preferred fix:** When `UseGlobalContractAction` is processed with `GlobalContractIdentifier::AccountId`, resolve and store the code hash at that moment (converting the account's contract field to `AccountContract::Global(resolved_hash)` instead of `AccountContract::GlobalByAccount(id)`). This makes the reference immutable after opt-in, matching the security model of `CodeHash` mode.

2. **Alternative:** Introduce a protocol-level invariant that `GlobalContractIdentifier::AccountId` redeployment is only permitted to update to code with the same ABI/interface hash, or require all existing users to re-opt-in after a redeployment.

3. **Minimum mitigation:** Document prominently that `AccountId` mode gives the deployer permanent, unilateral control over the code executed in every user account that opted in, and that users should prefer `CodeHash` mode for security.

### Proof of Concept

1. Alice deploys a legitimate global contract (e.g., a token contract) via `DeployGlobalContractAction` with `GlobalContractDeployMode::AccountId`. Code stored at `TrieKey::GlobalContractCode { identifier: AccountId("alice") }`.

2. Bob (and 1,000 other accounts) call `UseGlobalContractAction` with `GlobalContractIdentifier::AccountId("alice")`. Each account's state is set to `AccountContract::GlobalByAccount("alice")`.

3. Alice submits a second `DeployGlobalContractAction` with `GlobalContractDeployMode::AccountId` containing malicious WASM. `apply_distribution_current_shard` overwrites the trie key with the new code.

4. Any caller (including Alice herself) sends a `FunctionCall` receipt to Bob's account. `RuntimeContractIdentifier::resolve` looks up the current hash for `AccountId("alice")`, gets the malicious code hash, and executes it in Bob's account context.

5. The malicious code calls `promise_batch_action_transfer(bob_balance)` to Alice's account. Bob's NEAR balance is drained. The state root committed to the block reflects Bob's zeroed balance and Alice's increased balance — a permanent, consensus-finalized fund loss.

### Citations

**File:** runtime/runtime/src/global_contracts.rs (L93-95)
```rust
    let contract = match contract_identifier {
        GlobalContractIdentifier::CodeHash(code_hash) => AccountContract::Global(*code_hash),
        GlobalContractIdentifier::AccountId(id) => AccountContract::GlobalByAccount(id.clone()),
```

**File:** runtime/runtime/src/global_contracts.rs (L208-211)
```rust
    let trie_key = TrieKey::GlobalContractCode { identifier };
    let code_len = global_contract_data.code().len() as u64;
    state_update.set(trie_key, global_contract_data.code().to_vec());
    state_update.commit(StateChangeCause::ReceiptProcessing { receipt_hash: receipt.get_hash() });
```

**File:** runtime/runtime/src/contract_code.rs (L43-46)
```rust
        let local_hash = match GlobalContractIdentifier::try_from(account_contract) {
            Ok(gci) => {
                let code_hash = gci.clone().hash(state_update, access)?;
                return Ok(RuntimeContractIdentifier::Global { code_hash, identifier: gci });
```

**File:** runtime/runtime/src/contract_code.rs (L92-106)
```rust
    fn hash(self, store: &TrieUpdate, access: AccessOptions) -> Result<CryptoHash, StorageError> {
        if let GlobalContractIdentifier::CodeHash(hash) = self {
            return Ok(hash);
        }
        let key = TrieKey::GlobalContractCode { identifier: self.into() };
        let value_ref =
            store.get_ref(&key, KeyLookupMode::MemOrFlatOrTrie, access)?.ok_or_else(|| {
                let TrieKey::GlobalContractCode { identifier } = key else { unreachable!() };
                StorageError::StorageInconsistentState(format!(
                    "Global contract identifier not found {:?}",
                    identifier
                ))
            })?;
        Ok(value_ref.value_hash())
    }
```

**File:** test-loop-tests/src/tests/global_contracts.rs (L72-106)
```rust
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

**File:** runtime/runtime/src/lib.rs (L631-638)
```rust
                let account_contract = account.contract().into_owned();
                let contract_id = RuntimeContractIdentifier::resolve(
                    account_id,
                    account_contract,
                    &state_update,
                    &epoch_info_provider.chain_id(),
                    AccessOptions::DEFAULT,
                )?;
```
