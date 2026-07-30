## Finding

### Title
Unauthorized Lockup Account Squatting via Unsigned `owner_account_id` in `LockupFactory::create` - (File: `lockup-factory/src/lib.rs`)

### Summary
The `create` entrypoint of `LockupFactory` derives the address of the new lockup contract deterministically from an attacker-supplied `owner_account_id` argument, without requiring that `owner_account_id` to sign the transaction or otherwise prove control. Any unprivileged caller can therefore pre-create (squat) the lockup account for an arbitrary target `owner_account_id` before the legitimate deployment happens, permanently denying that account holder the ability to ever have their intended lockup/vesting contract deployed by the factory at that address.

### Finding Description
`create()` computes the child account name purely from a hash of the caller-supplied `owner_account_id`, with no signer/authorization check on that value: [1](#0-0) 

```rust
#[payable]
pub fn create(
    &mut self,
    owner_account_id: ValidAccountId,
    ...
) -> Promise {
    assert!(env::attached_deposit() >= MIN_ATTACHED_BALANCE, "Not enough attached deposit");

    let byte_slice = env::sha256(owner_account_id.as_ref().as_bytes());
    let lockup_account_id =
        format!("{}.{}", hex::encode(&byte_slice[..20]), env::current_account_id());
    ...
```

There is no assertion that `env::predecessor_account_id()` equals `owner_account_id`, and `owner_account_id` is only a `ValidAccountId` type (format validation only) — not a `Signer`. The only gate is `MIN_ATTACHED_BALANCE` (3.5 NEAR): [2](#0-1) 

The account creation itself is unconditional; there is no pre-check for whether the target `lockup_account_id` already exists before attempting `create_account()`: [3](#0-2) 

This is functionally identical to the reported analog: in the Solana report, the oracle PDA was derived from `admin.key()` without requiring `admin` to be a signer, letting an attacker pre-initialize the oracle account for a legitimate admin and permanently block their real initialization. Here, the lockup account's name is derived from `owner_account_id` without requiring that account to sign, letting an attacker pre-create the lockup account for a legitimate/expected token-grant recipient before the real (large-value, correctly-configured) lockup is deployed by the factory or by an operator script such as `scripts/deploy_lockup.sh`.

Because NEAR account names must be globally unique, and this factory always derives the same deterministic name (`sha256(owner_account_id)[..20]` + factory suffix) for a given `owner_account_id`, once an attacker's `create_account()` succeeds at that name, any subsequent legitimate `create()` call for the same `owner_account_id` will fail at the `create_account()` action (name already taken) and the deposit will be refunded via `on_lockup_create`: [4](#0-3) 

— but the intended owner is now permanently unable to obtain a properly configured lockup contract at their expected/reserved address through this factory.

### Impact Explanation
This is a permanent, irrecoverable denial-of-service against the legitimate lockup-creation flow for any targeted `owner_account_id` (e.g., a known future employee/token-grant recipient whose account ID is knowable in advance). The attacker can occupy the account with a minimal/arbitrary lockup configuration (e.g., zero lockup duration, no vesting), permanently preventing the foundation/operator from ever deploying the intended (larger, vesting-restricted) lockup contract at that deterministic address. This matches the in-scope impact category of account-binding failure in pool/account-creation flows breaking rightful, single-execution guarantees, and constitutes irrevocable loss of the intended lockup configuration for the targeted account.

### Likelihood Explanation
Likelihood is medium: exploitation only requires knowledge of a target's `owner_account_id` (often predictable/public prior to a grant, e.g. published employee or grantee account names) and a one-time deposit of `MIN_ATTACHED_BALANCE` (3.5 NEAR). No privileged role, signature from the victim, or race against block production beyond basic front-running is required — any unprivileged account can call the public `create` method directly.

### Recommendation
- Require the `owner_account_id` to be the transaction predecessor (i.e., `assert_eq!(env::predecessor_account_id(), owner_account_id.as_ref())`) so only the intended owner (or someone acting explicitly on their behalf with their signature) can claim their deterministic lockup slot, or
- Remove the deterministic 1:1 binding between `owner_account_id` and the lockup account name (e.g., include a nonce/random salt or the deposit amount/predecessor in the derivation) so the same `owner_account_id` can be retried under a fresh address if squatted, or
- Check whether `lockup_account_id` already exists and belongs to a legitimately-created lockup for that `owner_account_id` before allowing new `create()` calls to target it, rejecting collisions from unrelated callers upfront rather than relying on the promise callback to refund the loser.

### Proof of Concept
1. Attacker learns the target's future `owner_account_id`, e.g. `alice.near`, who is expected to later receive a legitimate lockup via `scripts/deploy_lockup.sh`.
2. Attacker calls `create(owner_account_id="alice.near", lockup_duration=0, lockup_timestamp=None, vesting_schedule=None, release_duration=None, whitelist_account_id=None)` on the factory, attaching `MIN_ATTACHED_BALANCE` (3.5 NEAR). Predecessor is the attacker's own account; no signature from `alice.near` is required.
3. The factory computes `lockup_account_id = sha256("alice.near")[..20] + "." + factory_account_id` and successfully creates/deploys a minimal lockup contract there.
4. When the foundation/operator later runs `deploy_lockup.sh` (or calls `create`) for the real grant to `alice.near`, the resulting `Promise::new(lockup_account_id).create_account()` fails because the account already exists; `on_lockup_create` detects failure and refunds the deposit, but `alice.near`'s intended lockup contract can never be created at the reserved address.

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

**File:** lockup-factory/src/lib.rs (L136-158)
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
