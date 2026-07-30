Based on the analysis, I have enough evidence to confirm this analog vulnerability.

### Title
Deterministic lockup account address squatting causes permanent DoS of legitimate lockup creation - (File: `lockup-factory/src/lib.rs`)

### Summary
The `LockupFactory::create()` function derives the sub-account ID for a new lockup contract solely as `sha256(owner_account_id)`, with no salt, nonce, or caller-binding. Because the function is `#[payable]` and callable by any unprivileged account, an attacker can call `create()` for a known/target `owner_account_id` before the legitimate party does, permanently occupying the deterministic address with attacker-chosen lockup parameters and preventing the rightful lockup contract from ever being deployed for that owner.

### Finding Description
`create()` computes the lockup account id purely from the `owner_account_id` argument: `let lockup_account_id = format!("{}.{}", hex::encode(&byte_slice[..20]), env::current_account_id());` [1](#0-0)  This is the NEAR-analog of a deterministic `CREATE2` address in the referenced report: the resulting sub-account name depends only on public, attacker-known input (`owner_account_id`), not on the predecessor/caller identity or any per-deployment nonce.

The function itself has no privileged-caller restriction—only a minimum attached deposit is required: `assert!(env::attached_deposit() >= MIN_ATTACHED_BALANCE, "Not enough attached deposit");` [2](#0-1)  Any unprivileged account can call `create()` with an arbitrary `owner_account_id` (e.g., a known investor/team address expected to receive an official lockup) and arbitrary `lockup_duration`, `vesting_schedule`, and `release_duration`, paying only the modest `MIN_ATTACHED_BALANCE` (3.5 NEAR): [3](#0-2) 

The subsequent account creation is a simple `Promise::new(lockup_account_id).create_account()...`: [4](#0-3)  If the attacker creates the account first, when the legitimate/intended `create()` call for the same `owner_account_id` later executes, the `create_account()` action fails because the account already exists on-chain. The failure is caught only in the callback, which refunds the deposit to the (legitimate) caller but does not create the intended lockup: [5](#0-4) 

Unlike `staking-pool-factory`, which at least tracks issued IDs in an on-chain `UnorderedSet` before dispatching the promise (`self.staking_pool_account_ids.insert(&staking_pool_account_id)`) [6](#0-5) , `LockupFactory::create()` has no such registry or reservation mechanism at all — there is nothing to even detect or reject a duplicate submission before the async account-creation promise is attempted.

Because `owner_account_id` is the sole determinant of the target address and there is no protocol-level restriction preventing an arbitrary account from creating a sub-account under the factory via the factory's own `create()` entrypoint, this exactly parallels the external report's root cause: a permissionless, deterministic deployment path that any unprivileged party can pre-empt to block the intended deployment.

### Impact Explanation
This is a permanent, irrecoverable DoS: since the lockup address is bound 1:1 to `owner_account_id` with no other differentiator, once an attacker has squatted `sha256(owner_account_id).<factory>`, the legitimate/intended lockup contract for that owner_account_id can never be created under this factory. This matches the "High: Replay, duplicate-effect ... in ... pool-creation ... flows that breaks single-execution guarantees" and, depending on treatment, could reach "Critical: Permanent freezing/unrecoverable lock of user funds in lockup release ... flows," since the token allocation intended for that specific owner can never be deposited into a correctly-configured lockup contract at the expected address — requiring a completely new, manual, off-protocol remediation (analogous to the referenced report requiring a second governance vote to redeploy).

### Likelihood Explanation
Likelihood is high. The `owner_account_id` values destined for lockup contracts (e.g., token sale participants, team/investor allocations) are frequently known or guessable in advance from public token distribution plans. The attack requires no front-running sophistication — the attacker can call `create()` for the target `owner_account_id` at any time before the legitimate creation transaction, using only a fixed, modest deposit (3.5 NEAR) and standard function-call permissions available to any account.

### Recommendation
Add a persistent on-chain registry of already-created (or in-flight) `lockup_account_id`s in `LockupFactory` (similar to `staking_pool_account_ids` in `staking-pool-factory`), and/or restrict `create()` to only be callable by the `foundation_account_id`/an authorized allocator, and/or check `env::current_account_id()`-scoped account existence before dispatching the creation promise so that pre-emptive squatting can be detected and handled explicitly (e.g., reverting clearly, or deriving the address using an additional caller/salt-bound component so squatting a specific owner's address in advance is not possible).

### Proof of Concept
1. Attacker observes (from public token allocation plans) that `owner_account_id = alice.near` is scheduled to receive an official lockup via `LockupFactory::create()`.
2. Attacker computes `lockup_account_id = hex::encode(sha256("alice.near")[..20]) + "." + factory_account_id` (the same deterministic formula in `create()`, lines 119–121).
3. Attacker calls `create(owner_account_id="alice.near", lockup_duration=..., vesting_schedule=None, ...)` themselves, attaching `MIN_ATTACHED_BALANCE`, before the foundation's official transaction executes.
4. The attacker's transaction creates the sub-account at the deterministic address with attacker-chosen (junk) lockup terms.
5. When the foundation later submits the intended `create("alice.near", <correct vesting schedule>, ...)` call, the `create_account()` promise action fails since the account already exists; `on_lockup_create` detects failure via `is_promise_success()` and refunds the foundation's deposit, but the correct lockup contract is never created — permanently blocking legitimate lockup deployment for `alice.near` under this factory instance.

### Citations

**File:** lockup-factory/src/lib.rs (L34-34)
```rust
const MIN_ATTACHED_BALANCE: Balance = 3_500_000_000_000_000_000_000_000;
```

**File:** lockup-factory/src/lib.rs (L117-117)
```rust
        assert!(env::attached_deposit() >= MIN_ATTACHED_BALANCE, "Not enough attached deposit");
```

**File:** lockup-factory/src/lib.rs (L119-121)
```rust
        let byte_slice = env::sha256(owner_account_id.as_ref().as_bytes());
        let lockup_account_id =
            format!("{}.{}", hex::encode(&byte_slice[..20]), env::current_account_id());
```

**File:** lockup-factory/src/lib.rs (L136-139)
```rust
        Promise::new(lockup_account_id.clone())
            .create_account()
            .deploy_contract(CODE.to_vec())
            .transfer(env::attached_deposit())
```

**File:** lockup-factory/src/lib.rs (L171-197)
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
```

**File:** staking-pool-factory/src/lib.rs (L166-170)
```rust
        assert!(
            self.staking_pool_account_ids
                .insert(&staking_pool_account_id),
            "The staking pool account ID already exists"
        );
```
