## Analog Vulnerability Found

### Title
Missing `assert_self()` guard on `on_staking_pool_create` allows an unprivileged attacker to drain the Staking Pool Factory's NEAR balance - (File: `staking-pool-factory/src/lib.rs`)

### Summary
The `Splitter.incrementWindow` bug in the external report stems from a callback-style function that trusts caller-supplied data without verifying that the caller is the legitimate, expected counterparty. The Staking Pool Factory contract has the same root cause: its promise-callback method `on_staking_pool_create` is `pub` and reachable by any account, but unlike every other callback in this codebase it never calls `assert_self()` to verify `predecessor_account_id() == current_account_id()`.

### Finding Description
`on_staking_pool_create` is declared as an ordinary public method meant to be invoked only as a `.then()` continuation of the factory's own `create_staking_pool` promise chain: [1](#0-0) 

Every other callback in this codebase (`lockup/src/owner_callbacks.rs`, `lockup/src/foundation_callbacks.rs`) explicitly calls `assert_self()` before trusting `is_promise_success()` and any accompanying state changes: [2](#0-1) 

`on_staking_pool_create`, however, has no such check. It only relies on `is_promise_success()`, which merely asserts that exactly one promise result exists in the current execution context: [3](#0-2) 

That precondition (`env::promise_results_count() == 1`) is trivially satisfiable by an attacker: they simply deploy their own contract, issue any promise (even one deliberately designed to fail, e.g. a transfer that exceeds balance or a call to a nonexistent method), and attach `.then()` to invoke `factory.on_staking_pool_create(staking_pool_account_id, attached_deposit, predecessor_account_id)` with fully attacker-chosen arguments — including `attached_deposit` and `predecessor_account_id`.

When the attacker engineers their upstream promise to fail, `is_promise_success()` returns `false`, and the factory executes:
```rust
self.staking_pool_account_ids.remove(&staking_pool_account_id);
...
Promise::new(predecessor_account_id).transfer(attached_deposit.0);
``` [4](#0-3) 

This transfers `attached_deposit.0` — an arbitrary, attacker-supplied amount — from the factory contract's own NEAR balance to `predecessor_account_id`, which the attacker also controls. There is no verification that this deposit was ever actually attached by a real `create_staking_pool` call.

Additionally, if the attacker instead engineers the upstream promise to succeed, the success branch calls `ext_whitelist::add_staking_pool` with an arbitrary `staking_pool_account_id` chosen by the attacker (not necessarily one created via a legitimate `create_staking_pool` deposit flow), which the whitelist contract will accept because the predecessor of that call is the trusted, already-whitelisted factory account: [5](#0-4) 

This lets an attacker get an arbitrary, attacker-controlled account whitelisted as a "trusted" staking pool without ever depositing the required 30 NEAR or passing through the real `create_staking_pool` creation/verification flow.

### Impact Explanation
This is a Critical finding under the allowed impact scope:
- Unauthorized transfer of NEAR out of the factory contract's balance via a public callback lacking caller authentication (direct fund theft), reachable by any unprivileged account.
- Unauthorized whitelisting of an attacker-controlled account as a "staking pool," which lockup contract owners rely on as a safety guarantee (`whitelist/README.md` states whitelisting is meant to ensure delegated tokens "can not be lost or locked"). A malicious whitelisted pool can subsequently be selected by unsuspecting lockup owners and used to permanently lock/steal delegated NEAR — matching the "permanent freezing/unrecoverable loss" and "unauthorized transfer" impact categories.

### Likelihood Explanation
Likelihood is high: exploitation requires only deploying a simple attacker-owned contract capable of issuing a promise chain — no privileged role, no leaked keys, and no interaction with any trusted party is needed. The precondition (`promise_results_count() == 1`) is met by any contract-to-contract call pattern, which is standard and freely available to any NEAR account.

### Recommendation
Add `assert_self()` at the start of `on_staking_pool_create`, mirroring the pattern used in `lockup/src/owner_callbacks.rs` and `lockup/src/foundation_callbacks.rs`, so the method can only be invoked as a genuine callback from the factory's own `create_staking_pool` promise chain: [6](#0-5) 

### Proof of Concept
1. Attacker deploys a helper contract `Evil`.
2. `Evil::attack()` issues `Promise::new(some_account).function_call(<nonexistent method>, ..., huge_gas)` (guaranteed to fail), and attaches `.then()` calling `factory.on_staking_pool_create(staking_pool_account_id="anything", attached_deposit=U128(huge_amount), predecessor_account_id="evil_receiver")`.
3. When the first promise fails, `is_promise_success()` returns `false` inside `on_staking_pool_create`, executing `Promise::new(predecessor_account_id).transfer(attached_deposit.0)`, draining `attached_deposit.0` yoctoNEAR from the factory contract to `evil_receiver`.
4. Alternatively, engineering the first promise to succeed causes the factory to call `ext_whitelist::add_staking_pool` with an attacker-chosen `staking_pool_account_id`, whitelisting an account the attacker fully controls as a "trusted" staking pool. [7](#0-6)

### Citations

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

**File:** lockup/src/owner_callbacks.rs (L29-33)
```rust
    pub fn on_staking_pool_deposit(&mut self, amount: WrappedBalance) -> bool {
        assert_self();

        let deposit_succeeded = is_promise_success();
        self.set_staking_pool_status(TransactionStatus::Idle);
```

**File:** staking-pool-factory/src/utils.rs (L7-17)
```rust
pub fn is_promise_success() -> bool {
    assert_eq!(
        env::promise_results_count(),
        1,
        "Contract expected a result on the callback"
    );
    match env::promise_result(0) {
        PromiseResult::Successful(_) => true,
        _ => false,
    }
}
```

**File:** whitelist/src/lib.rs (L75-88)
```rust
    pub fn add_staking_pool(&mut self, staking_pool_account_id: AccountId) -> bool {
        assert!(
            env::is_valid_account_id(staking_pool_account_id.as_bytes()),
            "The given account ID is invalid"
        );
        // Can only be called by a whitelisted factory or by the foundation.
        if !self
            .factory_whitelist
            .contains(&env::predecessor_account_id())
        {
            self.assert_called_by_foundation();
        }
        self.whitelist.insert(&staking_pool_account_id)
    }
```

**File:** lockup/src/foundation_callbacks.rs (L9-13)
```rust
    pub fn on_get_account_staked_balance_to_unstake(
        &mut self,
        #[callback] staked_balance: WrappedBalance,
    ) -> PromiseOrValue<bool> {
        assert_self();
```
