### Title
Missing failure-refund callback in `MultisigFactory::create` permanently locks attached NEAR deposit when sub-account creation fails - (File: `multisig-factory/src/lib.rs`)

### Summary
`MultisigFactory::create` builds a sub-account id by naive string concatenation (`format!("{}.{}", name, env::current_account_id())`) and fires a single fire-and-forget `Promise` batch (`create_account` → `deploy_contract` → `transfer` → `function_call`) without ever checking whether the batch succeeded. Every other factory contract in this repo (`lockup-factory`, `staking-pool-factory`) validates the composed account id and, critically, attaches a callback that checks `is_promise_success()` and refunds the attached deposit to the caller if the sub-account creation fails. `multisig-factory` has neither the validation nor the refund callback.

### Finding Description
In `multisig-factory/src/lib.rs`, `create()` never validates `name` before using it to build the sub-account id, unlike `staking-pool-factory::create_staking_pool` which explicitly rejects `.` in the id and calls `env::is_valid_account_id` on the resulting id, or `lockup-factory::create` which derives a guaranteed-valid hex sub-account name via `sha256`: [1](#0-0) 

Compare with the equivalent, safer patterns: [2](#0-1) [3](#0-2) 

More importantly, `staking-pool-factory` and `lockup-factory` both attach a `.then(...)` callback to self (`on_staking_pool_create` / `on_lockup_create`) that inspects `is_promise_success()` and, on failure, explicitly transfers the attached deposit back to `predecessor_account_id`: [4](#0-3) [5](#0-4) 

`multisig-factory::create` has no such callback at all — the `Promise` batch is simply returned to the runtime with no `.then(...)`: [6](#0-5) 

If the batch (`create_account`, `deploy_contract`, `transfer`, `function_call`) fails for any reason — the sub-account name already exists (e.g., two users race to use the same `name` prefix, since there is no on-chain registry check like `staking_pool_account_ids` in `staking-pool-factory`), `name` contains characters that make the concatenated id an invalid NEAR account id, or the account name exceeds length limits — the attached deposit that was moved into the receipt is not returned to the original caller. There is no callback to detect the failure and issue a refund, and `MultisigFactory` exposes no owner/admin method to recover such stranded balance.

### Impact Explanation
This is a permanent, irrecoverable loss of user funds for the calling account whenever a `create()` call's underlying account-creation receipt fails, with no way to reclaim the attached NEAR. This matches the in-scope Critical impact: "Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in ... factory refund ... flows." The sibling factories (`lockup-factory`, `staking-pool-factory`) explicitly implement refund-on-failure precisely because this outcome is otherwise possible in NEAR's action-batch model — `multisig-factory` simply omits that safety net.

### Likelihood Explanation
Likelihood is realistic and does not require any privileged access: any unprivileged user calling the public, payable `create` method can lose funds if their chosen `name` collides with an already-created (or concurrently being created) sub-account, which is an ordinary race condition in a public factory with no reservation/registry mechanism, or if their `name` produces an invalid resulting account id (e.g. containing disallowed characters, since `name` is an unchecked `AccountId`/`String`). No malicious intent is required for the loss to occur, and no owner action can retroactively fix it.

### Recommendation
Add a callback analogous to `on_lockup_create`/`on_staking_pool_create`: after the create-account batch, chain a `.then(ext_self::on_multisig_create(...))` that checks `is_promise_success()`, and if the sub-account creation failed, refunds `env::attached_deposit()` back to `env::predecessor_account_id()`. Additionally validate `name` up front (reject `.` and other disallowed characters, and/or verify `env::is_valid_account_id` on the composed id) before creating the promise batch, mirroring `staking-pool-factory::create_staking_pool`.

### Proof of Concept
1. User A calls `create(name="alice", members=[...], num_confirmations=1)` on `multisig-factory`, attaching `X` NEAR. The resulting account `alice.<factory>` does not yet exist, so this succeeds.
2. User B, in the same or an adjacent block, also calls `create(name="alice", members=[...], num_confirmations=1)` attaching `Y` NEAR before A's transaction is finalized (or after A's account already exists). The `create_account` action for `alice.<factory>` fails because the account already exists.
3. Because there is no `.then(...)` callback checking success, B's attached deposit `Y` is never returned to B; it is not applied to any created account and is not sent back to B's account. `MultisigFactory` has no owner or public method to withdraw or manually refund this stranded value, resulting in a permanent loss of `Y` NEAR for user B.

### Citations

**File:** multisig-factory/src/lib.rs (L28-49)
```rust
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

**File:** staking-pool-factory/src/lib.rs (L144-158)
```rust
        assert!(
            env::attached_deposit() >= MIN_ATTACHED_BALANCE,
            "Not enough attached deposit to complete staking pool creation"
        );

        assert!(
            staking_pool_id.find('.').is_none(),
            "The staking pool ID can't contain `.`"
        );

        let staking_pool_account_id = format!("{}.{}", staking_pool_id, env::current_account_id());
        assert!(
            env::is_valid_account_id(staking_pool_account_id.as_bytes()),
            "The staking pool account ID is invalid"
        );
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

**File:** lockup-factory/src/lib.rs (L117-121)
```rust
        assert!(env::attached_deposit() >= MIN_ATTACHED_BALANCE, "Not enough attached deposit");

        let byte_slice = env::sha256(owner_account_id.as_ref().as_bytes());
        let lockup_account_id =
            format!("{}.{}", hex::encode(&byte_slice[..20]), env::current_account_id());
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
