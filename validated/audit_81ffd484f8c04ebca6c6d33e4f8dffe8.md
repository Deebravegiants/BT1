### Title
Loss of attached deposit on failed multisig creation due to missing refund callback and front-runnable account name - (File: `multisig-factory/src/lib.rs`)

### Summary
`multisig-factory/src/lib.rs`'s `create()` function is the direct core-contracts analog of the DAOfi front-running bug: it deploys a new contract to a deterministic account name that depends only on an attacker-controllable parameter, and — unlike its sibling factories — never checks for a callback on creation failure to refund the depositor. Any unprivileged user can front-run a legitimate `create()` call (or simply cause it to fail) and permanently trap the caller's attached NEAR deposit inside the factory contract with no recovery path.

### Finding Description
`create()` builds the child account id purely from the attacker-supplied `name` argument and the factory's own account id, with no binding to `predecessor_account_id` or a hash of anything user-specific: [1](#0-0) 

Compare this to `staking-pool-factory/src/lib.rs`, which maintains a registry (`staking_pool_account_ids: UnorderedSet<AccountId>`) and asserts uniqueness before issuing the account-creation promise: [2](#0-1) 
and which registers a callback `on_staking_pool_create` that explicitly refunds the attached deposit back to `predecessor_account_id` if the underlying `create_account`/`deploy_contract`/`function_call` promise fails: [3](#0-2) 

Likewise `lockup-factory/src/lib.rs`'s `create()` derives the child account id from `sha256(owner_account_id)` (binding the address to a specific identity, mirroring the report's own recommendation to "add the owner information to the salt") and also chains `.then(ext_self::on_lockup_create(...))`, which refunds the deposit on failure: [4](#0-3) 

`multisig-factory::create()` has neither protection:
1. No uniqueness/registry check — anyone can call `create()` first with the same `name` (attacker-chosen `members`/`num_confirmations`, minimal deposit), consuming that account id before the legitimate user's transaction lands, exactly analogous to the attacker calling `DAOfiV1Factory.createPair()` directly to preempt the router.
2. No `.then()` callback at all on the returned `Promise`. When the batched `CreateAccount + DeployContract + Transfer + FunctionCall` receipt fails (e.g., because the account already exists due to front-running, or because `new()` on `multisig2` panics on invalid `members`/`num_confirmations`), the attached deposit — which was already credited to the factory contract's balance when the `#[payable]` call executed — is not returned to the original caller. There is no code path in this contract that ever refunds a failed creation, and the factory exposes no withdrawal function, so the funds become permanently stuck in the factory account.

### Impact Explanation
This matches the "Critical: Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in ... factory refund ... flows" impact category. An unprivileged, unprivileged attacker can either:
- Grief/front-run a legitimate `create()` call by claiming the same `name` first (no special privilege required, ordinary transaction), causing the victim's subsequent `create()` call to fail and its attached NEAR deposit to be irrecoverably lost inside the factory contract; or
- Simply exploit the fact that any organic failure of pool/account creation (e.g., a user submitting an unintended/invalid `members`/`num_confirmations` combination that panics `multisig2::new`) also results in unrecoverable loss of the attached deposit, since there is no failure-handling callback at all.

### Likelihood Explanation
Likelihood is high for the front-running variant: `create()` is `#[payable]` and callable by anyone, requires only a small attached deposit and normal transaction fees to preempt a specific `name`, and NEAR account names are globally observable in the mempool/finalized transactions, making front-running straightforward. The "any failure loses funds permanently" variant is even more likely to occur accidentally, without any attacker at all, since the contract has zero handling for promise failure.

### Recommendation
- Bind the derived account id to the caller's identity (e.g., include `predecessor_account_id` or a hash of it in the account name/salt), as already done in `lockup-factory`.
- Track already-created multisig account ids in a persistent registry and reject duplicate `create()` calls before issuing the promise, as already done in `staking-pool-factory`.
- Add a `.then()` callback to the returned `Promise` (mirroring `on_lockup_create` / `on_staking_pool_create`) that checks `is_promise_success()` and refunds `env::attached_deposit()` back to `env::predecessor_account_id()` if account creation, deployment, or initialization fails.

### Proof of Concept
1. Victim intends to create a multisig at `mywallet.multisig-factory.near` by calling `create(name: "mywallet", members: [...], num_confirmations: 2)` with an attached deposit (e.g., 5 NEAR) and submits the transaction.
2. Attacker observes the pending/mempool transaction (or simply predicts a commonly used name) and submits their own `create(name: "mywallet", members: [attacker_key], num_confirmations: 1)` call with a small attached deposit and higher gas price/priority so it lands first, successfully creating `mywallet.multisig-factory.near` under attacker control.
3. Victim's original transaction executes: `Promise::new("mywallet.multisig-factory.near").create_account()` fails because the account already exists; the batched receipt (including the `.transfer(env::attached_deposit())` action) fails as a whole.
4. Because `create()` in `multisig-factory/src/lib.rs` [5](#0-4)  has no `.then()` callback, the victim's 5 NEAR deposit — already added to the factory contract's balance when the payable call was invoked — is never returned to the victim; it remains permanently stranded in the `multisig-factory` contract account, which has no withdrawal mechanism.

### Citations

**File:** multisig-factory/src/lib.rs (L29-49)
```rust
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

**File:** staking-pool-factory/src/lib.rs (L166-170)
```rust
        assert!(
            self.staking_pool_account_ids
                .insert(&staking_pool_account_id),
            "The staking pool account ID already exists"
        );
```

**File:** staking-pool-factory/src/lib.rs (L197-239)
```rust
    /// Callback after a staking pool was created.
    /// Returns the promise to whitelist the staking pool contract if the pool creation succeeded.
    /// Otherwise refunds the attached deposit and returns `false`.
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

**File:** lockup-factory/src/lib.rs (L118-198)
```rust

        let byte_slice = env::sha256(owner_account_id.as_ref().as_bytes());
        let lockup_account_id =
            format!("{}.{}", hex::encode(&byte_slice[..20]), env::current_account_id());

        let mut foundation_account: Option<AccountId> = None;
        if vesting_schedule.is_some() {
            foundation_account = Some(self.foundation_account_id.clone());
        };

        // Defaults to the whitelist account ID given on init call.
        let staking_pool_whitelist_account_id = if let Some(account_id) = whitelist_account_id {
            account_id.into()
        } else {
            self.whitelist_account_id.clone()
        };

        let transfers_enabled: WrappedTimestamp = TRANSFERS_STARTED.into();
        Promise::new(lockup_account_id.clone())
            .create_account()
            .deploy_contract(CODE.to_vec())
            .transfer(env::attached_deposit())
            .function_call(
                b"new".to_vec(),
                near_sdk::serde_json::to_vec(&LockupArgs {
                    owner_account_id,
                    lockup_duration,
                    lockup_timestamp,
                    transfers_information: TransfersInformation::TransfersEnabled {
                        transfers_timestamp: transfers_enabled,
                    },
                    vesting_schedule,
                    release_duration,
                    staking_pool_whitelist_account_id,
                    foundation_account_id: foundation_account,
                })
                    .unwrap(),
                NO_DEPOSIT,
                gas::LOCKUP_NEW,
            )
            .then(ext_self::on_lockup_create(
                lockup_account_id,
                env::attached_deposit().into(),
                env::predecessor_account_id(),
                &env::current_account_id(),
                NO_DEPOSIT,
                gas::CALLBACK,
            ))
    }

    /// Callback after a lockup was created.
    /// Returns the promise if the lockup creation succeeded.
    /// Otherwise refunds the attached deposit and returns `false`.
    pub fn on_lockup_create(
        &mut self,
        lockup_account_id: AccountId,
        attached_deposit: U128,
        predecessor_account_id: AccountId,
    ) -> bool {
        assert_self();

        let lockup_account_created = is_promise_success();

        if lockup_account_created {
            env::log(
                format!("The lockup contract {} was successfully created.", lockup_account_id)
                    .as_bytes(),
            );
            true
        } else {
            env::log(
                format!(
                    "The lockup {} creation has failed. Returning attached deposit of {} to {}",
                    lockup_account_id, attached_deposit.0, predecessor_account_id
                )
                    .as_bytes(),
            );
            Promise::new(predecessor_account_id).transfer(attached_deposit.0);
            false
        }
    }
```
