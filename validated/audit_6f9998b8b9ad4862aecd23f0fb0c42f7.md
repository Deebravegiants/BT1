## Analog Found

### Title
Lockup account ID is derived only from `owner_account_id` with no sender/nonce binding, allowing front-running to permanently squat a beneficiary's lockup address - (File: `lockup-factory/src/lib.rs`)

### Summary
`LockupFactory::create` derives the deterministic lockup contract account name solely from `sha256(owner_account_id)`, with no dependency on `predecessor_account_id`, a nonce, or any other request-specific salt. [1](#0-0)  Because NEAR account creation is a `create_account()` receipt that fails if the account already exists, any unprivileged attacker can front-run a legitimate `create` call for a given `owner_account_id` and permanently occupy that exact account name with attacker-chosen lockup terms, blocking the real lockup from ever being created for that beneficiary through this factory. This mirrors the SEDA `deriveRequestId` finding: a fully deterministic identifier with no `msg.sender`/nonce binding lets an unprivileged party front-run and squat/block a legitimate actor's request.

### Finding Description
`create` computes:
```rust
let byte_slice = env::sha256(owner_account_id.as_ref().as_bytes());
let lockup_account_id = format!("{}.{}", hex::encode(&byte_slice[..20]), env::current_account_id());
``` [1](#0-0) 

`owner_account_id` is a public, attacker-supplied parameter of `create`, which is `#[payable]` and callable by anyone who attaches `MIN_ATTACHED_BALANCE`. [2](#0-1)  There is no requirement that the caller (`predecessor_account_id`) match `owner_account_id`, and no nonce/salt is mixed into the derived name. As a result, for any target `owner_account_id`, the resulting `lockup_account_id` is 100% predictable by any observer of the mempool/network.

An attacker can front-run a pending legitimate `create` transaction for a target `owner_account_id` with their own `create` call using the same `owner_account_id` but attacker-chosen `lockup_duration`, `lockup_timestamp`, `vesting_schedule`, and `release_duration`. Because `Promise::new(lockup_account_id).create_account()` will fail once the name is taken, the legitimate transaction's promise batch fails and the callback `on_lockup_create` merely refunds the depositor — it does not retry the create, does not use a different address, and the account name is now permanently occupied. [3](#0-2)  Since NEAR account names cannot be recreated once they exist, the canonical lockup address for that `owner_account_id` is now permanently unavailable to the legitimate creator (e.g. the foundation) for that factory, and can only ever hold the attacker-defined lockup terms.

This is the exact root-cause class described in the SEDA report — a deterministic identifier with no unique per-request binding (`msg.sender`/nonce equivalent) — reachable here through the fully public, unprivileged `create` entrypoint.

### Impact Explanation
This matches "Critical: Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release ... factory refund ... flows" — the legitimate lockup for a given beneficiary can never be created via this factory once squatted, and there is no recovery path (NEAR account names are immutable once created). It also matches "High: Replay/duplicate-effect/account-binding failure in ... pool-creation ... flows that breaks single-execution or rightful redemption guarantees," since the account-binding for lockup creation has no protection against a race from an unrelated party.

### Likelihood Explanation
The attack requires only watching the public mempool for `create` calls (or simply pre-emptively squatting known/expected `owner_account_id`s such as team/investor accounts whose lockups are anticipated) and sending a transaction with a higher gas price / faster inclusion attaching only `MIN_ATTACHED_BALANCE` (3.5 NEAR). [4](#0-3)  No privileged role, secret, or validator collusion is needed — this is directly reachable by any unprivileged account, making likelihood realistic wherever lockup creation timing/target accounts are predictable or observable in advance.

### Recommendation
Bind the derived lockup account id to more than just `owner_account_id` — e.g., require `predecessor_account_id == owner_account_id` (or another authorization check) before allowing account creation for that name, and/or incorporate a factory-tracked nonce/mapping so a squatted or failed creation can be retried under a different, still-associated address instead of being permanently blocked.

### Proof of Concept
1. Victim (e.g. NEAR Foundation) submits `create(owner_account_id = "alice.near", lockup_duration, ...)` with `MIN_ATTACHED_BALANCE` attached.
2. Attacker observes the pending transaction (or simply predicts that `alice.near` will eventually receive a lockup) and submits their own `create(owner_account_id = "alice.near", lockup_duration = <attacker-chosen>, vesting_schedule = <attacker-chosen or None>)` with a competitive/higher gas price, attaching only `MIN_ATTACHED_BALANCE`.
3. Both calls compute the same `lockup_account_id = sha256("alice.near")[..20] || "." || factory_account"` per [1](#0-0) . Whichever `create_account()` receipt lands first succeeds; the other's `create_account()` fails, causing `on_lockup_create` to log the failure and refund the depositor's balance rather than creating the lockup. [5](#0-4) 
4. The victim's legitimate lockup for `alice.near` can never be created again through this factory — the address is permanently occupied by the attacker's version with attacker-controlled lockup/vesting terms.

### Citations

**File:** lockup-factory/src/lib.rs (L34-34)
```rust
const MIN_ATTACHED_BALANCE: Balance = 3_500_000_000_000_000_000_000_000;
```

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
