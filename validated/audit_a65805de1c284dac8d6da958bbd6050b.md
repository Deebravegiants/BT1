## Analysis

The Story Protocol report's root cause is a **globally-scoped, content-derived, attacker-predictable identifier used as a uniqueness key with no binding to the legitimate caller**, letting an unprivileged actor permanently squat/poison that identifier before the legitimate user can use it. Searching NEAR core-contracts for an analogous pattern in the in-scope production files turns up a real, independent instance of the same bug class (account-binding failure / squatting via deterministic identifier) in `lockup-factory/src/lib.rs`.

### Title
Deterministic, Owner-Only-Derived Lockup Account ID Allows Unprivileged Front-Running/Squatting That Permanently Blocks Legitimate Lockup Creation - (File: `lockup-factory/src/lib.rs`)

### Summary
`LockupFactory::create()` derives the lockup contract's account ID solely from `sha256(owner_account_id)`, with no binding to the caller (funder), deposit amount, or any salt/nonce. Because this identifier is fully deterministic and predictable from a single public input, any unprivileged account can precompute it for a known target `owner_account_id` and race to create (squat) that exact account before the legitimate/intended funding transaction lands, permanently and irrevocably denying the correct lockup contract from ever being created for that owner via this factory.

### Finding Description
In `create()`, the lockup account ID is computed purely from the `owner_account_id` argument, which is public information known to anyone (an employee/investor NEAR account name): [1](#0-0) 

```
let byte_slice = env::sha256(owner_account_id.as_ref().as_bytes());
let lockup_account_id = format!("{}.{}", hex::encode(&byte_slice[..20]), env::current_account_id());
``` [2](#0-1) 

The factory has no notion of "already reserved for this owner" check beyond the underlying `CreateAccount` action's implicit uniqueness at the protocol level (an account can only be created once). Since `create()` is a public, unprivileged, `#[payable]` entrypoint that anyone can call with an arbitrary `owner_account_id` and the minimum attached deposit, an attacker can:

1. Observe or simply know a target `owner_account_id` that a legitimate funder intends to create a lockup for (e.g., a known employee account, negotiated off-chain, or even seen in the public mempool as classic front-running).
2. Call `create(owner_account_id, minimal lockup_duration, no vesting, ...)` themselves first, attaching just `MIN_ATTACHED_BALANCE`.
3. Their `create_account()` + `deploy_contract()` + `function_call("new", ...)` promise succeeds first, permanently claiming the exact deterministic account ID computed for that `owner_account_id`.
4. When the legitimate funder's transaction with the correct/larger vesting schedule and deposit later executes `create()` for the same `owner_account_id`, the resulting `Promise::new(lockup_account_id).create_account()` fails because the account already exists; `on_lockup_create` correctly detects the failure via `is_promise_success()` and refunds the deposit: [3](#0-2) 

However, the refund only returns the caller's tokens — it does not and cannot fix the fact that the deterministic address for that `owner_account_id` under this factory account is now permanently occupied by an attacker-created (minimal, wrong-parameter) lockup contract. There is no alternate identifier the legitimate funder can choose (unlike `staking-pool-factory`, where the caller picks an arbitrary `staking_pool_id` string and can simply retry with a different name — see `staking-pool-factory/src/lib.rs` lines 137-170, which uses `self.staking_pool_account_ids.insert(...)` keyed on a caller-chosen string, not a fixed hash of a third-party's ID).

This is the direct core-contracts analog of the reported bug class: a fixed, non-negotiable, publicly-derivable identifier is used as a single-use resource, and an unprivileged, un-authorized party can consume/burn it ahead of the rightful user with no recovery path, because the identifier has no binding to caller identity, nonce, or salt.

### Impact Explanation
This falls under the "Permanent freezing / unrecoverable lock ... in lockup release ... factory refund" impact category (Critical) and the "account-binding failure in ... pool-creation ... flows that breaks ... rightful redemption guarantees" category (High). The legitimate funder's deposit is refunded (no direct token theft), but the intended lockup contract for that specific `owner_account_id` can never be created through this factory again — the vesting schedule, lockup duration, and full-value deposit intended for that beneficiary are permanently blocked, since the deterministic account address is squatted with attacker-chosen (minimal/wrong) parameters that cannot be un-deployed or upgraded by the rightful owner or funder.

### Likelihood Explanation
Exploitation requires no privilege — `create()` is a fully public, unprivileged function callable by anyone with `MIN_ATTACHED_BALANCE` [4](#0-3) . Unlike the original report's scenario (which relies on mempool front-running), here the attacker does not even need to observe a pending transaction: because the address depends only on the public `owner_account_id`, the attacker can pre-emptively squat any known target's future lockup address at any time, making this arguably easier to exploit than classic front-running.

### Recommendation
Bind the generated lockup account ID to more than just the recipient's `owner_account_id` — e.g., include the funder's account, an explicit salt/nonce chosen by the funder, or require the caller to pre-register/claim the intended `owner_account_id` in a way that only an authorized party (e.g., the foundation account for vesting lockups, or the owner account itself via signature) can initiate. Alternatively, allow the caller to specify a unique prefix (as `staking-pool-factory` does) so the identifier isn't a deterministic, publicly-guessable function of a single third-party's public account ID.

### Proof of Concept
1. Attacker learns (publicly, off-chain) that `alice.near` will receive a lockup from `funder.near` via the `lockup.near` factory.
2. Attacker computes `lockup_account_id = hex(sha256("alice.near")[..20]) + ".lockup.near"` — fully derivable off-chain.
3. Attacker calls `create(owner_account_id="alice.near", lockup_duration=1, vesting_schedule=None, ...)` with `MIN_ATTACHED_BALANCE`, succeeding in creating and deploying the lockup contract at that exact address.
4. `funder.near` later calls `create(owner_account_id="alice.near", ...)` with the real vesting schedule and full deposit; the `create_account()` promise fails since the account exists, and `on_lockup_create` refunds `funder.near`'s deposit [5](#0-4) .
5. `alice.near`'s intended, correctly-configured lockup can never be created at this deterministic address through this factory again.

### Citations

**File:** lockup-factory/src/lib.rs (L34-34)
```rust
const MIN_ATTACHED_BALANCE: Balance = 3_500_000_000_000_000_000_000_000;
```

**File:** lockup-factory/src/lib.rs (L107-139)
```rust
    #[payable]
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
