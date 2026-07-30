### Title
Missing re-initialization guard in `LockupContract::new` allows any unprivileged account to reset lockup state and seize ownership - (File: `lockup/src/lib.rs`)

### Summary
`LockupContract::new` (the `#[init]` constructor at `lockup/src/lib.rs`, lines 180-243) is a public function with no `assert!(!env::state_exists())` guard and no predecessor/caller check. Every other production contract init function in this codebase (`multisig/src/lib.rs` L104, `staking-pool/src/lib.rs` L179, `staking-pool-factory/src/lib.rs` L106, `whitelist/src/lib.rs` L34, `lockup-factory/src/lib.rs` L80) explicitly asserts `!env::state_exists()` to prevent re-initialization. `lockup/src/lib.rs` is missing this guard entirely. [1](#0-0) 

### Finding Description
On NEAR, calling a public contract method does not require the caller to hold any access key on the receiving contract's account — anyone can send a `FunctionCall` action to any account's public methods. Because `new()` has:
1. No `assert!(!env::state_exists())` check (unlike sibling contracts in this repo), and
2. No predecessor/owner check,

any unprivileged external account can call `new` again on an already-initialized, already-funded lockup contract, exactly as the initial deployer would: [2](#0-1) 

This overwrites the entire persisted `LockupContract` struct: `owner_account_id` (settable to the attacker's own account), `lockup_information` (resets `termination_withdrawn_tokens` to 0 and can rewrite `transfers_information`), `vesting_information` (can be wiped to `None` or rewritten), and `staking_information` (reset to `None`, orphaning any funds actually delegated to a staking pool from the contract's own bookkeeping perspective).

Because `owner_account_id` is fully attacker-controlled in the re-init call, the attacker immediately becomes the "owner" of the contract and can subsequently invoke the owner-only methods in `lockup/src/owner.rs` (e.g. transfer/staking operations gated only by `owner_account_id == predecessor_account_id`), enabling withdrawal of the account's NEAR balance to themselves once transfers are enabled (or immediately if `TransfersInformation::TransfersEnabled` is set as part of the malicious re-init call, since the attacker fully controls the constructor arguments, including `transfers_information`).

This is analogous in root-cause class (an "incorrect/missing initialization guard" that resets critical accounting/ownership state) to the ZetaChain report, but manifests here as a directly-reachable, unprivileged, public-entrypoint authorization bypass rather than a chain-restart edge case — arguably more severe because it requires no special conditions (hard fork/reset) at all, just a single transaction.

### Impact Explanation
This maps to the "Critical" impact category: unauthorized transfer/withdrawal/release of locked/vested NEAR through a public-call/accounting failure reachable by an unprivileged user, and to the "High" category of unauthorized execution/state-transition bypass letting an unprivileged user act beyond intended authority. An attacker can seize `owner_account_id`, erase vesting/termination bookkeeping, and orphan/derail staking accounting, ultimately enabling unauthorized transfer of the locked NEAR balance to themselves.

### Likelihood Explanation
Likelihood is high: exploitation requires only a single public `FunctionCall` transaction to the target lockup account's `new` method with attacker-chosen arguments — no privileged key, no owner cooperation, and no special network condition is required. The only precondition is that the target lockup account does not already have a full-access key removed (irrelevant to the attack) and is a normal NEAR account reachable by any signer, which is the standard deployment model for this contract per `README.md`.

### Recommendation
Add the same re-initialization guard used elsewhere in the codebase to `lockup/src/lib.rs`'s `new()`:
```rust
assert!(!env::state_exists(), "The contract is already initialized");
```
placed at the very start of the function, mirroring `multisig/src/lib.rs` L104, `staking-pool/src/lib.rs` L179, `staking-pool-factory/src/lib.rs` L106, `whitelist/src/lib.rs` L34, and `lockup-factory/src/lib.rs` L80.

### Proof of Concept
1. NEAR Foundation deploys and initializes a lockup contract at `employee.lockup.near` with legitimate `owner_account_id`, vesting schedule, and locked balance (standard deployment flow shown in `README.md` lines 44-75).
2. Attacker (any funded NEAR account, e.g. `attacker.near`, with no keys on `employee.lockup.near`) submits a `FunctionCall` transaction:
   - `receiver_id`: `employee.lockup.near`
   - `method_name`: `new`
   - `args`: `{"owner_account_id": "attacker.near", "lockup_duration": "0", "transfers_information": {"TransfersEnabled": {"transfers_timestamp": "0"}}, "vesting_schedule": null, "staking_pool_whitelist_account_id": "<any valid existing account>"}`
   - No deposit or special access key required.
3. Because `lockup/src/lib.rs`'s `new()` (lines 180-243) never checks `env::state_exists()` nor validates predecessor identity, the call succeeds and completely overwrites the contract's persisted state, making `attacker.near` the new `owner_account_id` with transfers enabled and no vesting restriction.
4. Attacker then calls the owner-only transfer method from `lockup/src/owner.rs` (gated only by `owner_account_id == predecessor_account_id`) to move the contract's entire NEAR balance to their own account. [1](#0-0)

### Citations

**File:** lockup/src/lib.rs (L180-243)
```rust
    #[init]
    pub fn new(
        owner_account_id: AccountId,
        lockup_duration: WrappedDuration,
        lockup_timestamp: Option<WrappedTimestamp>,
        transfers_information: TransfersInformation,
        vesting_schedule: Option<VestingScheduleOrHash>,
        release_duration: Option<WrappedDuration>,
        staking_pool_whitelist_account_id: AccountId,
        foundation_account_id: Option<AccountId>,
    ) -> Self {
        assert!(
            env::is_valid_account_id(owner_account_id.as_bytes()),
            "The account ID of the owner is invalid"
        );
        assert!(
            env::is_valid_account_id(staking_pool_whitelist_account_id.as_bytes()),
            "The staking pool whitelist account ID is invalid"
        );
        if let TransfersInformation::TransfersDisabled {
            transfer_poll_account_id,
        } = &transfers_information
        {
            assert!(
                env::is_valid_account_id(transfer_poll_account_id.as_bytes()),
                "The transfer poll account ID is invalid"
            );
        }
        let lockup_information = LockupInformation {
            lockup_amount: env::account_balance(),
            termination_withdrawn_tokens: 0,
            lockup_duration: lockup_duration.0,
            release_duration: release_duration.map(|d| d.0),
            lockup_timestamp: lockup_timestamp.map(|d| d.0),
            transfers_information,
        };
        let vesting_information = match vesting_schedule {
            None => {
                assert!(
                    foundation_account_id.is_none(),
                    "Foundation account can't be added without vesting schedule"
                );
                VestingInformation::None
            }
            Some(VestingScheduleOrHash::VestingHash(hash)) => VestingInformation::VestingHash(hash),
            Some(VestingScheduleOrHash::VestingSchedule(vs)) => {
                VestingInformation::VestingSchedule(vs)
            }
        };
        assert!(
            vesting_information == VestingInformation::None ||
                env::is_valid_account_id(foundation_account_id.as_ref().unwrap().as_bytes()),
            "Foundation account should be added for vesting schedule"
        );

        Self {
            owner_account_id,
            lockup_information,
            vesting_information,
            staking_information: None,
            staking_pool_whitelist_account_id,
            foundation_account_id,
        }
    }
```
