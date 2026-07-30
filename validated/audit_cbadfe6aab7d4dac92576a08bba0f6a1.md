All in-scope production initializer functions (`new`) already guard against re-initialization:

- `lockup/src/lib.rs` — no explicit `state_exists` check is shown in the init in the snippet retrieved (lines 180-243), which is worth double-checking.
- `staking-pool/src/lib.rs:179` — `assert!(!env::state_exists(), "Already initialized");`
- `staking-pool-factory/src/lib.rs:106` — `assert!(!env::state_exists(), "The contract is already initialized");`
- `whitelist/src/lib.rs:34` — `assert!(!env::state_exists(), "Already initialized");`
- `multisig/src/lib.rs:104` — `assert!(!env::state_exists(), "Already initialized");`

Let me verify the lockup contract's `new` function specifically, since it didn't show the guard in the earlier snippet.Confirmed: `LockupContract::new` at `lockup/src/lib.rs:180-243` lacks the `assert!(!env::state_exists(), ...)` guard present in every other production contract's `#[init]` function in this repo (`staking-pool/src/lib.rs:179`, `staking-pool-factory/src/lib.rs:106`, `whitelist/src/lib.rs:34`, `multisig/src/lib.rs:104`, `lockup-factory/src/lib.rs:80`, `voting/src/lib.rs:36`). Since `owner_account_id`, `transfers_information`, `vesting_schedule`, and `foundation_account_id` are all caller-supplied parameters and `assert_owner()` (used to gate `transfer`, `add_full_access_key`, etc. in `lockup/src/owner.rs`) checks `self.owner_account_id`, any unprivileged account could re-invoke `new` after genuine deployment to overwrite state and appoint themselves owner with transfers immediately enabled, then drain the locked NEAR balance via `transfer`/`add_full_access_key`.

### Title
Lockup contract `new` initializer lacks re-initialization guard, allowing state takeover - (`lockup/src/lib.rs`)

### Summary
`LockupContract::new` (`lockup/src/lib.rs:180-243`) is a NEAR `#[init]` method but, unlike every other production contract in this repository, it does not check `env::state_exists()` before writing state. This mirrors the reported `Controller.initialize` bug class (missing initializer guard), and in NEAR's SDK the `#[init]` attribute by itself does not prevent a public `new` call from being invoked again after genuine deployment — an explicit `assert!(!env::state_exists(), ...)` is the idiomatic guard, as seen in `staking-pool/src/lib.rs:179`, `staking-pool-factory/src/lib.rs:106`, `whitelist/src/lib.rs:34`, `multisig/src/lib.rs:104`, `lockup-factory/src/lib.rs:80`, and `voting/src/lib.rs:36`.

### Finding Description
`new` accepts fully attacker-controllable arguments: `owner_account_id`, `transfers_information`, `vesting_schedule`, `release_duration`, `staking_pool_whitelist_account_id`, and `foundation_account_id` (`lockup/src/lib.rs:181-190`). It performs only input-format validation (valid account IDs, vesting/foundation consistency) and never checks `env::predecessor_account_id()` against any pre-existing owner, nor guards against the contract already being initialized. It then unconditionally overwrites `self` with the new `Self { owner_account_id, lockup_information, vesting_information, staking_information: None, staking_pool_whitelist_account_id, foundation_account_id }` (`lockup/src/lib.rs:235-242`), recomputing `lockup_amount` from the *current* `env::account_balance()` at call time.

Every owner-privileged action (`transfer`, `add_full_access_key`, `select_staking_pool`, `withdraw_from_staking_pool`, etc., in `lockup/src/owner.rs`) is gated solely by `assert_owner()`, which compares `env::predecessor_account_id()` to `self.owner_account_id` (`lockup/src/internal.rs:122-128`). Because `owner_account_id` can be rewritten by anyone re-calling `new`, an attacker can seize ownership of the lockup account and its held NEAR balance.

### Impact Explanation
This matches the Critical impact category: unauthorized transfer/withdrawal of locked NEAR through a public-call accounting failure reachable by an unprivileged user. An attacker calling `new` again can set `owner_account_id` to their own account and set `transfers_information` to `TransfersEnabled` with an immediate/past timestamp and no vesting schedule, then call `transfer` (`lockup/src/owner.rs:467-487`) to drain the contract's available NEAR balance to themselves, resulting in irrecoverable loss of the legitimate beneficiary's locked/vesting funds.

### Likelihood Explanation
`new` is a standard public contract method with no caller restriction and no re-initialization check, so any unprivileged NEAR account can call it directly against a live, already-initialized lockup account at any time after the legitimate initial deployment transaction completes. No privileged role, key compromise, or race condition beyond a normal subsequent transaction is required.

### Recommendation
Add `assert!(!env::state_exists(), "The contract is already initialized");` at the start of `LockupContract::new`, consistent with the guard already used in `staking-pool/src/lib.rs`, `staking-pool-factory/src/lib.rs`, `whitelist/src/lib.rs`, `multisig/src/lib.rs`, `lockup-factory/src/lib.rs`, and `voting/src/lib.rs`.

### Proof of Concept
1. Deploy/observe a live lockup contract account `lockup1` with legitimate `owner_account_id = "victim"` and locked NEAR balance.
2. From an unprivileged attacker account `attacker`, call:
   `near call lockup1 new '{"owner_account_id": "attacker", "lockup_duration": "0", "lockup_timestamp": null, "transfers_information": {"TransfersEnabled": {"transfers_timestamp": "0"}}, "vesting_schedule": null, "release_duration": null, "staking_pool_whitelist_account_id": "staking-pool-whitelist", "foundation_account_id": null}' --accountId=attacker`
3. This succeeds because no `state_exists` guard blocks re-initialization, overwriting `owner_account_id` to `attacker` and immediately enabling transfers with no vesting/lockup restriction.
4. Attacker calls `lockup1.transfer({"amount": ..., "receiver_id": "attacker"})`, which passes `assert_owner()` (`lockup/src/internal.rs:122-128`) since `attacker` is now `owner_account_id`, draining the contract's liquid NEAR balance. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8)

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

**File:** lockup/src/owner.rs (L467-487)
```rust
    pub fn transfer(&mut self, amount: WrappedBalance, receiver_id: AccountId) -> Promise {
        self.assert_owner();
        assert!(amount.0 > 0, "Amount should be positive");
        assert!(
            env::is_valid_account_id(receiver_id.as_bytes()),
            "The receiver account ID is invalid"
        );
        self.assert_transfers_enabled();
        self.assert_no_staking_or_idle();
        self.assert_no_termination();
        assert!(
            self.get_liquid_owners_balance().0 >= amount.0,
            "The available liquid balance {} is smaller than the requested transfer amount {}",
            self.get_liquid_owners_balance().0,
            amount.0,
        );

        env::log(format!("Transferring {} to account @{}", amount.0, receiver_id).as_bytes());

        Promise::new(receiver_id).transfer(amount.0)
    }
```

**File:** lockup/src/internal.rs (L122-128)
```rust
    pub fn assert_owner(&self) {
        assert_eq!(
            &env::predecessor_account_id(),
            &self.owner_account_id,
            "Can only be called by the owner"
        )
    }
```

**File:** staking-pool/src/lib.rs (L174-180)
```rust
    pub fn new(
        owner_id: AccountId,
        stake_public_key: Base58PublicKey,
        reward_fee_fraction: RewardFeeFraction,
    ) -> Self {
        assert!(!env::state_exists(), "Already initialized");
        reward_fee_fraction.assert_valid();
```

**File:** staking-pool-factory/src/lib.rs (L104-107)
```rust
    #[init]
    pub fn new(staking_pool_whitelist_account_id: AccountId) -> Self {
        assert!(!env::state_exists(), "The contract is already initialized");
        assert!(
```

**File:** whitelist/src/lib.rs (L32-35)
```rust
    #[init]
    pub fn new(foundation_account_id: AccountId) -> Self {
        assert!(!env::state_exists(), "Already initialized");
        assert!(
```

**File:** multisig/src/lib.rs (L102-105)
```rust
    #[init]
    pub fn new(num_confirmations: u32) -> Self {
        assert!(!env::state_exists(), "Already initialized");
        Self {
```

**File:** lockup-factory/src/lib.rs (L75-81)
```rust
    #[init]
    pub fn new(
        whitelist_account_id: ValidAccountId,
        foundation_account_id: ValidAccountId,
    ) -> Self {
        assert!(!env::state_exists(), "The contract is already initialized");
        assert!(
```

**File:** voting/src/lib.rs (L34-37)
```rust
    #[init]
    pub fn new() -> Self {
        assert!(!env::state_exists(), "The contract is already initialized");
        VotingContract {
```
