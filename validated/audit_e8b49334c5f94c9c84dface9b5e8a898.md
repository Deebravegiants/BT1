## Analysis

The external report describes a `payable` entrypoint (`sendZkSafeTransaction`) that accepts value but has no accounting path to move it forward or refund it on failure — so any attached ETH becomes permanently stuck. Looking across all `#[payable]` entrypoints in `core-contracts`, the pattern is deliberately mitigated everywhere **except** in `multisig-factory/src/lib.rs`.

Compare the three "factory" style `#[payable]` creation functions:

- `lockup-factory::create` transfers the deposit as part of an account-creation batch, and explicitly attaches a `.then(ext_self::on_lockup_create(...))` callback that checks `is_promise_success()` and refunds the attached deposit to `predecessor_account_id` if the sub-account creation failed. [1](#0-0) [2](#0-1) 

- `staking-pool-factory::create_staking_pool` follows the identical pattern: batch transfer + `on_staking_pool_create` callback that refunds on failure. [3](#0-2) [4](#0-3) 

- `multisig-factory::create`, however, performs `create_account().deploy_contract(CODE).transfer(env::attached_deposit()).function_call(...)` **with no `.then()` callback at all** — there is no success/failure check and no refund logic. [5](#0-4) 

`MultisigFactory` exposes no other public method (`get_*`, `withdraw`, etc.) capable of moving funds back out. [6](#0-5) 

### Title
Attached deposit is permanently lost when `MultisigFactory::create` fails to create the sub-account - (File: `multisig-factory/src/lib.rs`)

### Summary
`create` is `#[payable]` and forwards the entire `attached_deposit` inside the same promise batch used to create/deploy the new multisig account. Unlike the sibling `lockup-factory` and `staking-pool-factory` contracts, it has no completion callback to detect failure and refund the caller. If the batch fails for any reason (e.g. the target sub-account name already exists, is invalid, insufficient gas, or bad `stake`/`members` arguments), the attached NEAR is not returned to the caller and there is no method on the contract to reclaim it.

### Finding Description
`create_account`, `deploy_contract`, `transfer`, and `function_call` are chained as a single promise/action batch in `create`. [7](#0-6) 
If this batch fails (name collision, invalid account id, `CODE` deploy failure, etc.), the attached deposit is not delivered to the new account, and, critically, is never returned to the original `predecessor_account_id`. The contract defines no callback and no other public function capable of forwarding the balance back to the depositor, so the funds are stranded on the `MultisigFactory` contract account with no protocol-level way to recover them — mirroring exactly the root cause in the external report (a `payable` entrypoint with no accounting path for the attached value on the failure/no-op branch).

An unprivileged attacker can trigger this deterministically by front-running: watching the mempool (or simply pre-registering) for a desired sub-account name (`{name}.{multisig-factory}`) and creating it first, guaranteeing that any subsequent legitimate `create(name, ...)` call with the same `name` will fail its `CreateAccount` action and permanently strand the victim's attached deposit.

### Impact Explanation
This matches the "Critical: Permanent freezing, unrecoverable lock, or irrevocable loss of user ... funds in ... factory refund ... flows" category. Any user calling `create` with an insufficient/failing outcome loses their entire attached deposit irrecoverably through the public interface.

### Likelihood Explanation
The attack requires no privilege — any unprivileged account can grief a target `name` by registering the sub-account first, or a user can simply pass a name that already exists. This is directly reachable through the sole public payable entrypoint of the contract.

### Recommendation
Add a callback (mirroring `on_lockup_create`/`on_staking_pool_create`) that checks `is_promise_success()` after the account-creation batch and, on failure, issues `Promise::new(predecessor_account_id).transfer(attached_deposit)` to refund the caller, consistent with the pattern already used in `lockup-factory` and `staking-pool-factory`.

### Proof of Concept
1. Attacker calls `create("alice", [...], 1)` (or otherwise ensures `alice.multisig-factory` exists) without needing to actually finish a legitimate multisig — even an intentionally malformed call that gets the account created suffices.
2. Victim later calls `create("alice", members, num_confirmations)` with an attached deposit to create their own multisig.
3. The `CreateAccount` action fails because `alice.multisig-factory` already exists; the whole batch (including the `Transfer` action carrying the victim's deposit) fails.
4. `MultisigFactory` has no callback logic to detect this failure and no method to refund or withdraw, so the victim's deposit remains stuck on the factory contract with no path to recovery via the public interface. [5](#0-4)

### Citations

**File:** lockup-factory/src/lib.rs (L136-165)
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
```

**File:** lockup-factory/src/lib.rs (L171-198)
```rust
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

**File:** staking-pool-factory/src/lib.rs (L172-196)
```rust
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

**File:** multisig-factory/src/lib.rs (L22-49)
```rust
#[near_bindgen]
#[derive(BorshSerialize, BorshDeserialize, Default)]
pub struct MultisigFactory {}

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
