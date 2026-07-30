### Title
Permanent Denial-of-Service of Lockup Creation via Front-Running the Deterministic Lockup Account ID - (File: `lockup-factory/src/lib.rs`)

### Summary
`LockupFactory::create()` is a fully public, unprivileged, `#[payable]` entrypoint that computes the new lockup contract's account ID deterministically from a caller-supplied `owner_account_id` and creates the account via `Promise::new(lockup_account_id).create_account()`. Because NEAR account creation is a one-shot operation that fails if the target account ID already exists, and because `create()` performs no reservation check or restriction on who may call it (unlike the foundation/factory-privileged flows elsewhere in the repo), any unprivileged attacker can pre-empt the deterministic address for an arbitrary victim `owner_account_id`, permanently preventing the legitimate (foundation-sponsored) lockup/vesting contract for that owner from ever being created at that address.

### Finding Description
`create()` derives the lockup account name purely from a `sha256` hash of the user-supplied `owner_account_id`: [1](#0-0) 

There is no check that the caller (`env::predecessor_account_id()`) is the foundation, an authorized party, or that this specific `owner_account_id` has not already been "claimed." The only gate is a minimum attached deposit: [2](#0-1) 

The resulting account ID is entirely deterministic and collision-prone by design (`sha256(owner_account_id)[..20].<factory>`), and NEAR's runtime `create_account()` action fails permanently for an already-existing account ID (accounts, once created on NEAR, cannot be "re-created" or overwritten). The callback only handles the failure by refunding the deposit — it does not, and cannot, recover the account namespace: [3](#0-2) 

An unprivileged attacker can therefore:
1. Predict or learn a victim employee/investor's `owner_account_id` that the NEAR Foundation intends to grant a real vesting/lockup contract to (before the Foundation's transaction executes).
2. Call `create()` themselves with that same `owner_account_id`, attaching only the `MIN_ATTACHED_BALANCE` (3.5 NEAR), and arbitrary/garbage lockup parameters (no vesting schedule, `lockup_duration = 0`, etc.).
3. This pre-creates and permanently occupies `sha256(owner_account_id)[..20].<factory>` with a bogus, attacker-chosen lockup contract.
4. When the Foundation later calls `create()` for the same `owner_account_id` with the real vesting schedule and full token allocation, the `create_account()` promise action fails because the account already exists, `on_lockup_create` detects `is_promise_success() == false`, and the Foundation's deposit is refunded — but the real vesting/lockup contract for that employee can never be deployed at the (only possible, deterministic) address under this factory.

This is directly analogous to the reported Gearbox pattern: an unprivileged actor claims/occupies a resource slot (there: `creditFacade`'s "account ownership" via `openCreditAccount`; here: the deterministic lockup account namespace via `create()`) that a privileged process later needs exclusive use of, and the privileged process's own state-machine assumption (an address can only be initialized once) turns into an irreversible block once violated by the attacker.

### Impact Explanation
This is a "state-machine / input-binding" failure: the account-ID binding derived from user input has no authorization or reservation step, so an unprivileged party can permanently deny a specific victim from ever receiving their intended vesting/lockup contract through this factory. This matches the in-scope impact "Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release, vesting termination, ... factory refund ... flows" and the "account-binding failure in ... pool-creation ... flows that breaks single-execution or rightful redemption guarantees" bucket — the intended employee/investor can never obtain their contractual vesting/lockup account via the canonical factory flow, a form of denial that is not self-inflicted and is irrecoverable for that specific `owner_account_id`.

### Likelihood Explanation
The attack is cheap (only the 3.5 NEAR minimum deposit is required, which is refunded on legitimate failure attempts but consumed/locked in the attacker's bogus contract otherwise), requires no privileged role, and only requires the attacker to know or predict the target `owner_account_id` ahead of the Foundation's transaction (e.g., watching the mempool, or knowing onboarding naming conventions for upcoming employee/investor accounts). Because `create()` has no allowlist or predecessor check, likelihood is high for any targeted victim account whose id is known in advance.

### Recommendation
Restrict `create()` (or at least the ability to determine/claim a given `owner_account_id`'s deterministic slot) to the foundation account, or introduce a reservation/allowlist mechanism so that only an authorized caller can create a lockup contract for a specific `owner_account_id`. Alternatively, incorporate a factory-controlled nonce/salt (not fully attacker-predictable/front-runnable) into the account ID derivation, or require a two-step commit-reveal/registration process so that only the authorized principal (or an entity chosen by the foundation) can consume the deterministic slot for a given owner.

### Proof of Concept
1. Foundation intends to grant employee `alice.near` a lockup contract via `LockupFactory::create()`.
2. Attacker observes/predicts `owner_account_id = "alice.near"` will be used and front-runs by calling:
   ```
   near call factory.near create '{"owner_account_id": "alice.near", "lockup_duration": "0"}' --accountId attacker.near --amount 3.5
   ```
   This creates `sha256("alice.near")[..20].factory.near` with the attacker's chosen (garbage) parameters.
3. Foundation's later legitimate call:
   ```
   near call factory.near create '{"owner_account_id": "alice.near", "vesting_schedule": {...}}' --accountId foundation.near --amount 35
   ```
   resolves to the exact same account ID; `create_account()` fails because the account already exists; `on_lockup_create` refunds the foundation's deposit per [4](#0-3) , and Alice can never receive her real vesting/lockup contract through this factory.

### Citations

**File:** lockup-factory/src/lib.rs (L107-121)
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
