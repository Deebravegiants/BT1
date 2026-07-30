### Title
Lockup contract `new()` initializer is missing the `state_exists` re-initialization guard, allowing anyone to re-initialize an already-deployed lockup contract - (File: lockup/src/lib.rs)

### Summary
This is a direct analog of the reported `ERC20Facet.initialize` issue (missing "not already initialized" check). In `core-contracts`, every other in-scope `#[init]` constructor (`staking-pool`, `staking-pool-factory`, `whitelist`, `multisig`, `lockup-factory`) explicitly guards against re-initialization with `assert!(!env::state_exists(), "...")`, but the lockup contract's `new()` does not have this check. [1](#0-0) 

Compare with the other constructors that all include the guard: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

### Finding Description
`near-bindgen` exposes every `pub fn` on the contract struct, including `#[init]` methods, as a publicly callable method that any account can invoke via a `FunctionCall` action targeting the lockup contract's account ID — the caller does not need to hold any key belonging to the lockup account itself. The `new()` constructor takes attacker-controllable parameters (`owner_account_id`, `transfers_information`, `vesting_schedule`, `foundation_account_id`, `staking_pool_whitelist_account_id`) and unconditionally overwrites the entire persisted `LockupContract` state with a freshly built struct: [7](#0-6) 

Because there is no `assert!(!env::state_exists(), ...)` (or any predecessor/owner check) at the top of `new()`, an unprivileged, unrelated attacker can call `new` a second time on an already-deployed and funded lockup contract, setting:
- `owner_account_id` to their own account,
- `transfers_information` to `TransfersEnabled { transfer_timestamp: <past timestamp> }`,
- `vesting_schedule` to `None` (bypassing any vesting/foundation lock),
- `lockup_timestamp`/`release_duration` to values that make funds immediately available.

`lockup_information.lockup_amount` is set from `env::account_balance()` at call time, so it captures the full existing balance of the (already funded) lockup account.

All subsequent owner-privileged operations (e.g. `transfer` in `lockup/src/owner.rs`) authorize solely based on `self.owner_account_id`, via `assert_owner()`: [8](#0-7) 

Since the attacker has just overwritten `owner_account_id` to their own account and enabled transfers, `assert_owner()` and `assert_transfers_enabled()` both pass for the attacker, letting them call `transfer` (`lockup/src/owner.rs`) and drain the account's NEAR balance to themselves.

### Impact Explanation
This matches "Critical: Unauthorized transfer, withdrawal, spending, or release of locked... NEAR through public-call... accounting failure reachable by an unprivileged user" and "Critical: Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release... flows." An unprivileged attacker can seize ownership of any deployed lockup contract and steal its entire locked NEAR balance, bypassing lockup timestamps, vesting schedules, and foundation termination controls entirely.

### Likelihood Explanation
High likelihood: the attack requires only a single `FunctionCall("new", ...)` transaction to the target lockup contract account, no special privileges, keys, or races are needed, and it is directly reachable by any external account at any time after the lockup contract has been deployed and funded (which is the intended long-term state of every lockup contract in production).

### Recommendation
Add the same guard used in the other contracts to `lockup/src/lib.rs`'s `new()`:
```rust
assert!(!env::state_exists(), "The contract is already initialized");
```
This should be inserted at the very start of the function body, before any other logic, mirroring `staking-pool/src/lib.rs`, `staking-pool-factory/src/lib.rs`, `whitelist/src/lib.rs`, `multisig/src/lib.rs`, and `lockup-factory/src/lib.rs`.

### Proof of Concept
1. Deploy and initialize a lockup contract normally via `lockup-factory`, funding it with locked NEAR tokens (owner = victim).
2. As an unrelated attacker account, submit a `FunctionCall` transaction to the lockup contract's account with method `new` and arguments:
   - `owner_account_id`: attacker's account
   - `transfers_information`: `{ "TransfersEnabled": { "transfer_timestamp": "0" } }`
   - `vesting_schedule`: `null`
   - `lockup_duration`: `"0"`, `lockup_timestamp`: `null`, `release_duration`: `null`
   - `staking_pool_whitelist_account_id`: any valid whitelist account
   - `foundation_account_id`: `null`
3. Because `new()` never checks `env::state_exists()`, the call succeeds and overwrites the contract state, setting `owner_account_id` to the attacker and unlocking transfers immediately.
4. Attacker calls `transfer` (owner-only method, guarded by `assert_owner`) on `lockup/src/owner.rs`, which now succeeds because `self.owner_account_id` is the attacker's account, draining the contract's NEAR balance to the attacker.

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

**File:** whitelist/src/lib.rs (L32-34)
```rust
    #[init]
    pub fn new(foundation_account_id: AccountId) -> Self {
        assert!(!env::state_exists(), "Already initialized");
```

**File:** multisig/src/lib.rs (L102-104)
```rust
    #[init]
    pub fn new(num_confirmations: u32) -> Self {
        assert!(!env::state_exists(), "Already initialized");
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
