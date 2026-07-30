## Analysis

The external report's root cause is: a public account-creation entrypoint accepts a caller-chosen ID with no uniqueness reservation and no refund path when creation fails, letting an attacker front-run the ID and cause the victim to lose funds. `core-contracts--008` has a direct analog in `multisig-factory/src/lib.rs`.

### Title
Unrecoverable loss of user deposit when `MultisigFactory::create()` name collides with an existing account - (File: `multisig-factory/src/lib.rs`)

### Summary
`multisig-factory`'s `create()` function lets any unprivileged caller pick an arbitrary `name`, forms `account_id = "{name}.{factory}"`, and batches `create_account()`, `deploy_contract()`, `transfer(attached_deposit)`, and `function_call("new", ...)` into a single Promise, with no existence check and no completion callback.

### Finding Description
`create()` is fully public and unprivileged: [1](#0-0)  builds the target account id from an attacker/user-controlled `name` and attaches the caller's deposit directly inside a single atomic Promise chain (`create_account().deploy_contract(CODE.to_vec()).transfer(env::attached_deposit()).function_call(...)`), [2](#0-1) .

Unlike `staking-pool-factory`, which reserves the chosen name up front via `self.staking_pool_account_ids.insert(&staking_pool_account_id)` (reverting the whole call before any deposit is spent if the id is taken) and additionally wires a `.then()` callback `on_staking_pool_create` to detect promise failure and refund the depositor [3](#0-2) [4](#0-3) , `multisig-factory::create()` has:
- No pre-check that `account_id` doesn't already exist.
- No `.then()` callback to detect the created-account receipt's success/failure.

If `account_id` already exists — because an attacker observes the victim's pending `create()` transaction (same front-running pattern as the external report: listen for the transaction, then submit a competing call reserving the same target ID first) or simply predicts/squats a popular `name` — the `create_account()` action inside the batched receipt fails. Because all actions in that receipt are atomic, `transfer(env::attached_deposit())` also fails, but the balance was already deducted from the `multisig-factory` contract's own account balance when the receipt was created. Per NEAR receipt-refund semantics, that balance is refunded to the *predecessor of the failed receipt* — the `multisig-factory` contract account itself — not to the original caller (`env::predecessor_account_id()` of the `create()` call). Since there is no callback analogous to `on_staking_pool_create`, no code path ever forwards that refunded balance back to the user.

### Impact Explanation
The user's attached NEAR deposit becomes permanently and irrecoverably absorbed into the `multisig-factory` contract's balance, with no on-chain mechanism to reclaim it. This matches the Critical impact: "Permanent freezing, unrecoverable lock, or irrevocable loss of user ... funds in ... factory refund ... flows." The attacker gains nothing directly (pure griefing), but any unprivileged user can also self-trigger it accidentally by naming collision, and any unprivileged attacker can deliberately trigger it against a targeted victim by front-running the chosen `name`.

### Likelihood Explanation
Likelihood is high: `create()` is a completely public, unauthenticated entrypoint; the `name` parameter is entirely attacker/user chosen and unvalidated; front-running a pending `create()` transaction only requires mempool/transaction observation (identical precondition to the reported cross-chain bug) and a normal function call with a higher/competing gas price or same-block ordering advantage. No privileged role, key leakage, or external dependency compromise is needed.

### Recommendation
- Reserve the `account_id` in contract state before issuing the promise (as `staking-pool-factory` does with `staking_pool_account_ids.insert`), reverting up-front if already created/reserved, so the deposit is never spent on a doomed action.
- Add a `.then()` callback on the create-account promise that checks `is_promise_success()` and, on failure, transfers the attached deposit back to `env::predecessor_account_id()`, mirroring `staking-pool-factory::on_staking_pool_create`.

### Proof of Concept
1. Victim submits `create({"name": "alice", "members": [...], "num_confirmations": 2})` to `multisig-factory` with an attached deposit (e.g. 100 NEAR).
2. Attacker observes the pending transaction and submits `create({"name": "alice", ...})` with a minimal deposit, which lands first and successfully creates `alice.multisig-factory`.
3. Victim's transaction executes: `create_account()` for `alice.multisig-factory` fails because the account now exists; the whole batched receipt (including the 100 NEAR `transfer`) fails atomically.
4. The 100 NEAR is refunded to `multisig-factory`'s own balance (the receipt predecessor), not to the victim, and since `create()` has no callback to detect the failure, the victim's 100 NEAR is permanently lost.

### Citations

**File:** multisig-factory/src/lib.rs (L26-49)
```rust
#[near_bindgen]
impl MultisigFactory {
    #[payable]
    pub fn create(
        &mut self,
        name: AccountId,
        members: Vec<MultisigMember>,
        num_confirmations: u64,
    ) -> Promise {
        let account_id = format!("{}.{}", name, env::current_account_id());
        Promise::new(account_id)
            .create_account()
            .deploy_contract(CODE.to_vec())
            .transfer(env::attached_deposit())
            .function_call(
                b"new".to_vec(),
                json!({ "members": members, "num_confirmations": num_confirmations })
                    .to_string()
                    .as_bytes()
                    .to_vec(),
                0,
                env::prepaid_gas() - CREATE_CALL_GAS,
            )
    }
```

**File:** staking-pool-factory/src/lib.rs (L160-195)
```rust
        assert!(
            env::is_valid_account_id(owner_id.as_bytes()),
            "The owner account ID is invalid"
        );
        reward_fee_fraction.assert_valid();

        assert!(
            self.staking_pool_account_ids
                .insert(&staking_pool_account_id),
            "The staking pool account ID already exists"
        );

        Promise::new(staking_pool_account_id.clone())
            .create_account()
            .transfer(env::attached_deposit())
            .deploy_contract(include_bytes!("../../staking-pool/res/staking_pool.wasm").to_vec())
            .function_call(
                b"new".to_vec(),
                near_sdk::serde_json::to_vec(&StakingPoolArgs {
                    owner_id,
                    stake_public_key,
                    reward_fee_fraction,
                })
                .unwrap(),
                NO_DEPOSIT,
                gas::STAKING_POOL_NEW,
            )
            .then(ext_self::on_staking_pool_create(
                staking_pool_account_id,
                env::attached_deposit().into(),
                env::predecessor_account_id(),
                &env::current_account_id(),
                NO_DEPOSIT,
                gas::CALLBACK,
            ))
    }
```

**File:** staking-pool-factory/src/lib.rs (L200-239)
```rust
    pub fn on_staking_pool_create(
        &mut self,
        staking_pool_account_id: AccountId,
        attached_deposit: U128,
        predecessor_account_id: AccountId,
    ) -> PromiseOrValue<bool> {
        assert_self();

        let staking_pool_created = is_promise_success();

        if staking_pool_created {
            env::log(
                format!(
                    "The staking pool @{} was successfully created. Whitelisting...",
                    staking_pool_account_id
                )
                .as_bytes(),
            );
            ext_whitelist::add_staking_pool(
                staking_pool_account_id,
                &self.staking_pool_whitelist_account_id,
                NO_DEPOSIT,
                gas::WHITELIST_STAKING_POOL,
            )
            .into()
        } else {
            self.staking_pool_account_ids
                .remove(&staking_pool_account_id);
            env::log(
                format!(
                    "The staking pool @{} creation has failed. Returning attached deposit of {} to @{}",
                    staking_pool_account_id,
                    attached_deposit.0,
                    predecessor_account_id
                ).as_bytes()
            );
            Promise::new(predecessor_account_id).transfer(attached_deposit.0);
            PromiseOrValue::Value(false)
        }
    }
```
