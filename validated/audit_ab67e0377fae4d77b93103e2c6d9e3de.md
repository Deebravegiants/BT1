## Title
Weak Address Derivation in `LockupFactory::create` Enables Front-Running DoS/Hijack of Vesting Lockup Contracts - (File: `lockup-factory/src/lib.rs`)

### Summary
`LockupFactory::create` derives the deterministic sub-account address of the new lockup contract solely from `owner_account_id`, while ignoring all other caller-supplied parameters that materially affect the contract's initialization (`lockup_duration`, `lockup_timestamp`, `vesting_schedule`, `release_duration`, `whitelist_account_id`). Because the function has no access control and only requires a minimum attached deposit, any unprivileged actor can front-run a legitimate `create` call for a known `owner_account_id` and permanently occupy that deterministic address with attacker-chosen (degenerate) vesting terms, exactly mirroring the reported `VaultFactory::createVault` weak-salt issue.

### Finding Description
In `LockupFactory::create`, the lockup account address is computed as: [1](#0-0) 

This hash depends only on `owner_account_id`. However, the function accepts several additional parameters that determine the actual lockup semantics but are *not* part of the address: [2](#0-1) 

The function is `#[payable]` and public, with no access-control check beyond a minimum deposit: [3](#0-2) 

Since account IDs on NEAR must be unique, and this function performs `Promise::new(lockup_account_id).create_account()...`, only the *first* transaction targeting a given `owner_account_id` can ever succeed: [4](#0-3) 

Because `owner_account_id` values are typically known in advance (published vesting agreements, employee/investor account names, etc.), an attacker can observe or predict a legitimate `owner_account_id` about to be used and front-run the legitimate creator's transaction with the same `owner_account_id` but attacker-chosen `lockup_duration`, `vesting_schedule`, and `release_duration` (e.g. no vesting schedule at all, or a pathological/never-releasing schedule), while attaching only the minimum required deposit `MIN_ATTACHED_BALANCE`: [5](#0-4) 

Once the attacker's account-creation promise succeeds, the legitimate creator's later call to `create` for the same `owner_account_id` will fail at `create_account()` (account already exists) and simply be refunded via the callback: [6](#0-5) 

The refund prevents outright fund loss for the *factory call itself*, but the deterministic address for that `owner_account_id` is now permanently squatted with attacker-controlled vesting terms, and can never be re-created by the legitimate party through the factory.

### Impact Explanation
This is a direct DoS/hijack analog of the `VaultFactory` report: an unprivileged attacker can permanently block the deployment of a correctly configured lockup/vesting contract for any specific `owner_account_id`, or replace it with a contract that has attacker-chosen (weaker or degenerate) vesting/lockup parameters at the exact address the foundation/whitelist and downstream tooling expect. If the foundation or an off-chain process later assumes the contract at that deterministic address enforces the intended `vesting_schedule`/`lockup_duration` and transfers additional locked NEAR to it, those funds could be released on attacker-favorable (e.g., non-vesting) terms — a loss of the intended lock/vesting guarantee. At minimum this is a persistent, unrecoverable griefing/DoS against legitimate lockup creation for a targeted account.

### Likelihood Explanation
`create` is a fully public, unauthenticated, payable method callable by anyone with a small deposit (`MIN_ATTACHED_BALANCE`, 3.5 NEAR). `owner_account_id` values for planned lockups are generally known ahead of time (e.g., published grant recipients), making this attack straightforward and repeatable for any target owner whenever a new lockup contract is about to be created.

### Recommendation
Include all initialization parameters that affect the lockup's semantics (`lockup_duration`, `lockup_timestamp`, `vesting_schedule`, `release_duration`, `whitelist_account_id`) — or at minimum a caller/foundation-provided salt — in the derivation of `lockup_account_id`, so that only an exact match of parameters can occupy a given deterministic address. Alternatively, restrict `create` to only be callable by a trusted/foundation-controlled account (as is effectively assumed by the vesting design), rather than allowing arbitrary unprivileged callers to deploy lockup contracts for arbitrary `owner_account_id`s.

### Proof of Concept
1. Foundation/legitimate user intends to call `LockupFactory::create(owner_account_id="alice.near", lockup_duration=X, vesting_schedule=Some(real_schedule), ...)` with a large attached deposit covering the vested amount.
2. Attacker observes this pending transaction (or simply knows `alice.near` is a planned grantee) and submits `LockupFactory::create(owner_account_id="alice.near", lockup_duration=0, vesting_schedule=None, ...)` with only `MIN_ATTACHED_BALANCE` attached, using a higher gas price to be included first.
3. Attacker's transaction succeeds: `Promise::new(sha256("alice.near")[..20].hex() + "." + factory).create_account()...` deploys a lockup contract with no real vesting restriction at the deterministic address for `alice.near`.
4. The legitimate transaction from step 1 now fails at `create_account()` since the account already exists; `on_lockup_create` detects failure via `is_promise_success()` and refunds the attached deposit to the legitimate caller, but the address for `alice.near` is permanently occupied by the attacker's malicious lockup configuration, and no properly vested lockup contract can ever be created for `alice.near` via this factory.

### Citations

**File:** lockup-factory/src/lib.rs (L34-34)
```rust
const MIN_ATTACHED_BALANCE: Balance = 3_500_000_000_000_000_000_000_000;
```

**File:** lockup-factory/src/lib.rs (L108-121)
```rust
    pub fn create(
        &mut self,
        owner_account_id: ValidAccountId,
        lockup_duration: WrappedDuration,
        lockup_timestamp: Option<WrappedTimestamp>,
        vesting_schedule: Option<VestingScheduleOrHash>,
        release_duration: Option<WrappedDuration>,
        whitelist_account_id: Option<ValidAccountId>,
    ) -> Promise {
        assert!(env::attached_deposit() >= MIN_ATTACHED_BALANCE, "Not enough attached deposit");

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
