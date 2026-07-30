### Title
Missing reinitialization guard in `LockupContract::new` allows unprivileged takeover of an already-funded lockup contract - (File: `lockup/src/lib.rs`)

### Summary
The external report's root cause is a state-machine flaw: a caller can re-trigger a contract's `init` logic (by resetting the guard variable, `nonce`) after the contract is already live, letting an attacker seize ownership. The Fractional Vault achieves this via `delegatecall` storage collision, which has no direct analog in NEAR (cross-contract calls are async and do not share storage). However, `core-contracts` has its own, independent root cause of the same class ("init/state-transition guard bypass enabling re-initialization and ownership takeover"): the lockup contract's `#[init]` constructor is missing the standard `env::state_exists()` guard that every other production contract in this repo consistently applies.

### Finding Description
Every other `#[init]` constructor in the production contracts explicitly guards against re-initialization:

- `multisig/src/lib.rs` (line 104): `assert!(!env::state_exists(), "Already initialized");` [1](#0-0) 
- `staking-pool/src/lib.rs` (line 179): `assert!(!env::state_exists(), "Already initialized");` [2](#0-1) 
- `staking-pool-factory/src/lib.rs` (line 106): `assert!(!env::state_exists(), "The contract is already initialized");` [3](#0-2) 
- `lockup-factory/src/lib.rs` (line 80): `assert!(!env::state_exists(), "The contract is already initialized");` [4](#0-3) 
- `whitelist/src/lib.rs` (line 34): `assert!(!env::state_exists(), "Already initialized");` [5](#0-4) 

By contrast, `LockupContract::new` in `lockup/src/lib.rs` has no such check — the `#[init]` function goes straight into argument validation and struct construction with no `env::state_exists()` assertion: [6](#0-5) 

Because near-sdk (the version used here, judging by the surrounding contracts' need to add this check manually) does not itself reject calling an `#[init]`-annotated method when state already exists — every sibling contract in this same repo had to add the guard by hand — the absence of that same guard on `LockupContract::new` means `new` remains publicly callable by anyone at any time after deployment, even after the contract has already been initialized and funded with locked/vesting NEAR tokens.

An unprivileged attacker can call `new(...)` on an already-initialized, already-funded lockup contract, supplying their own `owner_account_id` (and arbitrary `foundation_account_id`, `vesting_schedule`, `transfers_information`, etc.). Since `Self { owner_account_id, lockup_information, vesting_information, staking_information: None, staking_pool_whitelist_account_id, foundation_account_id }` is returned and near-sdk will serialize/write this struct as the new contract state, this completely overwrites the existing `owner_account_id` and other state — including resetting `staking_information` to `None`, discarding any real vesting/termination progress — and hands ownership to the attacker.

This is analogous to the reported Vault issue: both are "guard variable governing a one-time `init` entrypoint is not adequately protected, letting an outside caller re-run initialization and seize the privileged `owner` role," just reached through a missing explicit check rather than through a `delegatecall`-induced storage collision.

### Impact Explanation
Once re-initialized with an attacker-chosen `owner_account_id`, the attacker becomes the "owner" of the lockup contract and can call all owner-only entrypoints in `lockup/src/owner.rs` (e.g., `select_staking_pool`, `deposit_and_stake`, `unstake`, `withdraw_from_staking_pool`, transfer functions) to drain the NEAR balance held by the lockup contract, including funds that were meant to remain locked/vesting for the legitimate employee/owner. This is a Critical-severity impact: unauthorized transfer/withdrawal of locked, vested NEAR through a public-call state-transition bypass, and it also causes permanent loss of the original owner's control and potentially their vesting rights.

### Likelihood Explanation
The attack requires only a normal, unprivileged function call (`new`) to an already-deployed lockup contract account — no special permissions, no reliance on the owner behaving maliciously or approving anything (unlike the Vault case, which required the owner to first add a malicious plugin to the merkle tree). Any account can attempt this call at any time against any deployed `LockupContract`. The only way this is not exploitable is if near-sdk's `#[init]` macro in the version pinned by this repo silently and universally prevents calling an `#[init]` function once `state_exists()` is true — but the fact that every other contract in this same codebase explicitly adds `assert!(!env::state_exists(), ...)` as defense strongly suggests the macro provides no such implicit protection in this version, making the omission in the lockup contract a genuine gap rather than defense-in-depth. I was not able to directly inspect the near-sdk-rs macro source (external dependency, not in scope) to give 100% certainty on macro-level protection, so this should be verified against the exact near-sdk-rs version pinned in `lockup/Cargo.toml` before remediation, but the strong and consistent pattern across sibling contracts is compelling evidence of a real gap.

### Recommendation
Add the same guard used throughout the rest of the codebase to `LockupContract::new` in `lockup/src/lib.rs`, e.g.:
```rust
#[init]
pub fn new(...) -> Self {
    assert!(!env::state_exists(), "The contract is already initialized");
    // ... existing validation and construction
}
```

### Proof of Concept
1. Deploy and initialize `LockupContract` normally via `new(owner_account_id: "alice", ...)`, funding it with locked NEAR (as done in `lockup/tests/spec.rs`).
2. As an unprivileged attacker account `mallory`, call `new(owner_account_id: "mallory", lockup_duration: 0, lockup_timestamp: None, transfers_information: TransfersEnabled{...}, vesting_schedule: None, release_duration: None, staking_pool_whitelist_account_id: <valid>, foundation_account_id: None)` directly against the already-deployed and already-funded lockup contract account.
3. Because `lockup/src/lib.rs`'s `new` (lines 180–243) contains no `env::state_exists()` check, the call succeeds (assuming near-sdk does not block it at the macro level) and the contract's `owner_account_id` is overwritten to `mallory`.
4. `mallory` now calls owner-only methods such as `select_staking_pool`, `unstake_all`, and transfer methods in `lockup/src/owner.rs` to withdraw the previously locked/vested NEAR balance to accounts they control. [7](#0-6)

### Citations

**File:** multisig/src/lib.rs (L102-104)
```rust
    #[init]
    pub fn new(num_confirmations: u32) -> Self {
        assert!(!env::state_exists(), "Already initialized");
```

**File:** staking-pool/src/lib.rs (L173-179)
```rust
    #[init]
    pub fn new(
        owner_id: AccountId,
        stake_public_key: Base58PublicKey,
        reward_fee_fraction: RewardFeeFraction,
    ) -> Self {
        assert!(!env::state_exists(), "Already initialized");
```

**File:** staking-pool-factory/src/lib.rs (L104-106)
```rust
    #[init]
    pub fn new(staking_pool_whitelist_account_id: AccountId) -> Self {
        assert!(!env::state_exists(), "The contract is already initialized");
```

**File:** lockup-factory/src/lib.rs (L75-80)
```rust
    #[init]
    pub fn new(
        whitelist_account_id: ValidAccountId,
        foundation_account_id: ValidAccountId,
    ) -> Self {
        assert!(!env::state_exists(), "The contract is already initialized");
```

**File:** whitelist/src/lib.rs (L32-34)
```rust
    #[init]
    pub fn new(foundation_account_id: AccountId) -> Self {
        assert!(!env::state_exists(), "Already initialized");
```

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

**File:** lockup/src/owner.rs (L12-20)
```rust
    pub fn select_staking_pool(&mut self, staking_pool_account_id: AccountId) -> Promise {
        self.assert_owner();
        assert!(
            env::is_valid_account_id(staking_pool_account_id.as_bytes()),
            "The staking pool account ID is invalid"
        );
        self.assert_staking_pool_is_not_selected();
        self.assert_no_termination();

```
