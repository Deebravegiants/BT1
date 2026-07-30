## Title
Missing refund-on-failure callback in `MultisigFactory::create` permanently traps user's attached NEAR - (File: `multisig-factory/src/lib.rs`)

### Summary
`MultisigFactory::create` in [1](#0-0)  forwards the caller's entire `attached_deposit()` into a cross-contract account-creation promise but, unlike its sibling factories (`lockup-factory` and `staking-pool-factory`), it has no callback to detect a failed account creation and refund the deposit to the original caller. If the underlying `create_account`/`deploy_contract`/`function_call` batch fails, the attached NEAR is refunded by the NEAR runtime to the *factory contract itself* (the predecessor of that receipt), not to the user, and the factory exposes no method to recover or forward that balance — the funds are permanently stuck.

### Finding Description
Compare the three factory `create` implementations:

- `lockup-factory/src/lib.rs` attaches a `.then(ext_self::on_lockup_create(...))` callback that checks `is_promise_success()` and explicitly `Promise::new(predecessor_account_id).transfer(attached_deposit.0)` if creation failed: [2](#0-1) .
- `staking-pool-factory/src/lib.rs` implements the identical refund-on-failure pattern via `on_staking_pool_create`: [3](#0-2) .
- `multisig-factory/src/lib.rs::create` has **no such callback at all** — it just issues the promise batch and returns it directly: [1](#0-0) .

When `create_account`/`deploy_contract`/`function_call("new", ...)` fails on the new sub-account (e.g., the sub-account name already exists, or the `new` initializer panics), the entire batched receipt fails as a unit. Under NEAR's protocol semantics, the balance attached to a failed receipt is refunded to the **predecessor of that receipt**, which is `multisig-factory` itself (since it was `multisig-factory` that called `Promise::new(account_id)`), not the original transaction signer. Since `MultisigFactory` is a stateless, ownerless contract (`pub struct MultisigFactory {}` [4](#0-3) ) with no function to withdraw or forward such a stray balance, the deposit becomes permanently unrecoverable.

A concrete trigger for the `new` initializer to panic is the assertion in `multisig2`'s constructor, which any caller can violate simply by passing `num_confirmations` greater than `members.len()`: [5](#0-4) . Because `create` is `#[payable]` and unauthenticated/unprivileged (any account can call it), an ordinary user who mis-specifies parameters, or whose chosen sub-account name collides with an existing account, will have their attached NEAR silently absorbed into the factory's balance with no path to reclaim it.

### Impact Explanation
This matches the "Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds ... in ... factory refund ... flows" Critical impact category. The attached deposit sent through a public, unprivileged entrypoint (`create`) is lost with no recovery mechanism — a direct analog to the reported GammaProtocol issue where ETH sent with a call became permanently stuck due to the absence of a withdrawal/refund path.

### Likelihood Explanation
Likelihood is realistic: unlike the original ETH bug (which required the user to simply overpay), the sibling factories (`lockup-factory`, `staking-pool-factory`) demonstrate that account-creation failures for these kinds of factories are an expected, handled failure mode — proving this isn't a purely theoretical edge case. Any user creating a multisig with a duplicate/likely name, or providing `num_confirmations > members.len()`, will trigger the loss deterministically and without any special privilege.

### Recommendation
Add a callback to `MultisigFactory::create` mirroring `lockup-factory`'s and `staking-pool-factory`'s pattern: chain `.then(ext_self::on_multisig_create(env::attached_deposit().into(), env::predecessor_account_id(), ...))`, check `is_promise_success()`, and `Promise::new(predecessor_account_id).transfer(attached_deposit)` when creation failed.

### Proof of Concept
1. Unprivileged user `alice` calls `multisig-factory.create({ name: "mysig", members: [...2 members...], num_confirmations: 3 })` with an attached deposit (e.g., 5 NEAR).
2. The generated `new` call on `mysig.multisig-factory` hits `assert(members.len() >= num_confirmations, ...)` in `multisig2/src/lib.rs` and panics [6](#0-5) .
3. The whole batched receipt (`create_account`, `deploy_contract`, `transfer`, `function_call`) fails; the 5 NEAR attached to the `transfer` action is refunded by the protocol to `multisig-factory`'s own account balance.
4. `alice` never receives her 5 NEAR back — `multisig-factory` has no function to withdraw or forward this balance to her, and there is no owner/admin capable of intervening, so the funds are permanently lost.

### Citations

**File:** multisig-factory/src/lib.rs (L22-24)
```rust
#[near_bindgen]
#[derive(BorshSerialize, BorshDeserialize, Default)]
pub struct MultisigFactory {}
```

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

**File:** lockup-factory/src/lib.rs (L136-198)
```rust
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

**File:** multisig2/src/lib.rs (L147-152)
```rust
    #[init]
    pub fn new(members: Vec<MultisigMember>, num_confirmations: u32) -> Self {
        assert(
            members.len() >= num_confirmations as usize,
            "Members list must be equal or larger than number of confirmations",
        );
```
