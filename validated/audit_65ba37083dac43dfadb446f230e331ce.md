### Title
`DeployGlobalContract` with `AccountId` Mode Lacks Ownership Check, Allowing Any Account to Overwrite Another Account's Global Contract — (File: `runtime/runtime/src/global_contracts.rs`)

### Summary
The `DeployGlobalContract` action with `GlobalContractDeployMode::AccountId` is documented as allowing "the owner to update the contract for all its users." However, `action_deploy_global_contract` performs no check that the action's predecessor (caller) equals the receiver (account owner). Any unprivileged account can send a `DeployGlobalContract(AccountId, malicious_code)` receipt targeting any victim account, overwriting the victim's globally-registered contract. Every account that references the victim's contract via `GlobalContractIdentifier::AccountId(victim)` will subsequently execute the attacker's code.

### Finding Description

**Design intent vs. implementation gap.**
`GlobalContractDeployMode::AccountId` is explicitly documented as:
> "Contract is deployed under the owner account id. Users will be able reference it by that account id. **This allows the owner to update the contract for all its users.**"

The identifier for the global contract in this mode is derived from `account_id`, which is the **receipt receiver**, not the predecessor (caller). In `initiate_distribution`: [1](#0-0) 

```rust
let id = match deploy_mode {
    GlobalContractDeployMode::CodeHash => {
        GlobalContractIdentifier::CodeHash(hash(&contract_code))
    }
    GlobalContractDeployMode::AccountId => {
        GlobalContractIdentifier::AccountId(account_id.clone())  // receiver, not predecessor
    }
};
```

**Missing authorization check.**
`action_deploy_global_contract` performs only a balance check (storage cost deduction) and then calls `initiate_distribution`. There is no check that `predecessor_id == receiver_id`: [2](#0-1) 

By contrast, the NEAR runtime enforces `predecessor_id == receiver_id` (the `ActorNoPermission` guard) for `DeployContract`, `Stake`, `AddKey`, `DeleteKey`, and `DeleteAccount`. The OpenAPI description confirms: [3](#0-2) 

> "Administrative actions like `DeployContract`, `Stake`, `AddKey`, `DeleteKey`. can be proceed only if sender=receiver…"

`DeployGlobalContract` is absent from this list.

**Attack path.**
1. Attacker (Alice) constructs a signed transaction: `signer_id = alice`, `receiver_id = bob`, `actions = [DeployGlobalContract { code: malicious_wasm, deploy_mode: AccountId }]`.
2. The runtime converts this to a receipt with `predecessor_id = alice`, `receiver_id = bob`.
3. `action_deploy_global_contract` is called with `account_id = bob`. The only check is whether Bob has enough balance to cover storage cost — which is deducted from Bob's account.
4. `initiate_distribution` creates `GlobalContractIdentifier::AccountId("bob")` and writes Alice's malicious code to `TrieKey::GlobalContractCode { identifier: AccountId("bob") }` across all shards.
5. Every account whose `AccountContract` is `GlobalByAccount("bob")` now executes Alice's code on the next function call.

The distribution mechanism propagates the overwrite to all shards via `GlobalContractDistributionReceipt`: [4](#0-3) 

The on-chain nonce is incremented by the attacker's deploy, so the attacker's version wins the freshness check on every shard: [5](#0-4) 

### Impact Explanation

**Corrupted protocol value:** `TrieKey::GlobalContractCode { identifier: GlobalContractCodeIdentifier::AccountId(victim) }` — the Wasm bytecode executed by every account that opted into the victim's global contract.

**Concrete impact:** The attacker's Wasm runs with full host-function access on every account that calls a method while using `GlobalContractIdentifier::AccountId(victim)`. The attacker can call `promise_batch_action_transfer` to drain balances, `promise_batch_action_delete_account` to destroy accounts, or exfiltrate storage. This is a direct, unconditional fund-loss path for all users of the victim's global contract — analogous to the `WellUpgradeable` finding where any caller could

### Citations

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

**File:** chain/jsonrpc/openapi/openapi.json (L1796-1820)
```json
          {
            "additionalProperties": false,
            "description": "Administrative actions like `DeployContract`, `Stake`, `AddKey`, `DeleteKey`. can be proceed only if sender=receiver\nor the first TX action is a `CreateAccount` action",
            "properties": {
              "ActorNoPermission": {
                "properties": {
                  "account_id": {
                    "$ref": "#/components/schemas/AccountId"
                  },
                  "actor_id": {
                    "$ref": "#/components/schemas/AccountId"
                  }
                },
                "required": [
                  "account_id",
                  "actor_id"
                ],
                "type": "object"
              }
            },
            "required": [
              "ActorNoPermission"
            ],
            "type": "object"
          },
```
