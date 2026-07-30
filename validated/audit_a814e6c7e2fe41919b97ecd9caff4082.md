### Title
`LockupContract::new()` lacks re-initialization guard, allowing owner takeover and theft of locked/vested NEAR - (File: `lockup/src/lib.rs`)

### Summary
`LockupContract::new()` is missing the `assert!(!env::state_exists(), ...)` guard that every other `#[init]` constructor in this codebase implements. This mirrors the external `BuilderWallet::init()` finding: an unprotected initializer that can be re-invoked post-deployment to overwrite the privileged account field (`owner_account_id`), which then gates all fund-moving "owner methods."

### Finding Description
Every other contract in this repo protects its `#[init]` constructor against re-invocation with an explicit `assert!(!env::state_exists(), "Already initialized")` (or equivalent) check:
- `lockup-factory/src/lib.rs` `new()`: `assert!(!env::state_exists(), "The contract is already initialized");` [1](#0-0) 
- `multisig/src/lib.rs` `new()`: `assert!(!env::state_exists(), "Already initialized");` [2](#0-1) 
- `staking-pool/src/lib.rs` `new()`: `assert!(!env::state_exists(), "Already initialized");` [3](#0-2) 
- `staking-pool-factory/src/lib.rs` `new()`: `assert!(!env::state_exists(), "The contract is already initialized");` [4](#0-3) 
- `whitelist/src/lib.rs` `new()`: `assert!(!env::state_exists(), "Already initialized");` [5](#0-4) 

`LockupContract::new()` in `lockup/src/lib.rs`, however, has no such check anywhere in the function body — it performs only argument-format validation (`is_valid_account_id`, vesting/foundation consistency) before unconditionally building and returning a fresh `Self`: [6](#0-5) 

In near-sdk-rs of this era, `#[init]` is purely a codegen marker for the constructor entry point; it does **not** itself prevent the method from being called again after state already exists — that protection has to be added manually via `env::state_exists()`, exactly as done in every sibling contract. Because `lockup/src/lib.rs`'s `new()` omits this check, any account (unprivileged) can call `new` again on an already-initialized, already-funded lockup contract and have it overwrite `owner_account_id`, `staking_pool_whitelist_account_id`, `vesting_information`, `staking_information` (reset to `None`), and `lockup_information` (recomputed from `env::account_balance()`), replacing all prior state with attacker-supplied fields.

All fund-moving methods in `lockup/src/owner.rs` are gated purely on `self.assert_owner()`, i.e., a check against the (now attacker-controlled) `owner_account_id` field: `select_staking_pool` [7](#0-6) , `unselect_staking_pool` [8](#0-7) , and further owner methods for deposit/stake/unstake/withdraw/transfer visible in `owner.rs`. Once `owner_account_id` is overwritten via a second `new()` call, the attacker legitimately passes `assert_owner()` and can drive the owner-authorized flows (deposit_and_stake/unstake/withdraw/transfer) to move the contract's NEAR balance to itself.

### Impact Explanation
This is a Critical finding matching the allowed impact scope ("Unauthorized transfer, withdrawal, spending, or release of locked, vested, pooled ... NEAR through public-call ... accounting failure reachable by an unprivileged user"). Any deployed lockup/vesting contract holding locked or vested NEAR can have its `owner_account_id` hijacked by any unprivileged caller, after which the attacker can drive owner-only withdrawal/transfer flows to steal the contract's entire NEAR balance — directly analogous to the `BuilderWallet.init()`/`sweep()` takeover pattern in the external report.

### Likelihood Explanation
High. The entrypoint (`new`) is a public, unauthenticated `#[init]` method on every deployed `LockupContract` account, requiring no privileged role, signer, or special conditions — only a standard `function_call("new", ...)` transaction against the already-deployed lockup account, exactly the same call shape used at legitimate deployment time (see `lockup-factory/src/lib.rs`'s deployment call to `b"new"` at deployment: `RiskEngine`-analog is `lockup-factory` here). The lack of the `state_exists` guard is a direct, structural code omission relative to every sibling contract in the same repo, not a theoretical or environment-dependent condition.

### Recommendation
Add the same guard used elsewhere in the codebase at the very start of `LockupContract::new()`:
```rust
assert!(!env::state_exists(), "The contract is already initialized");
```
in `lockup/src/lib.rs` before any other logic in the `new()` constructor.

### Proof of Concept
1. Deploy `LockupContract` via `lockup-factory`'s `create(...)`, which calls `new(...)` with `owner_account_id = victim` and funds the account with locked NEAR: [9](#0-8) 
2. Attacker (any unprivileged account) directly calls `new()` again on the deployed lockup account:
   ```
   near call <lockup_account_id> new '{
     "owner_account_id": "attacker.near",
     "lockup_duration": "0",
     "transfers_information": {"TransfersEnabled": {"transfers_timestamp": "0"}},
     "staking_pool_whitelist_account_id": "whitelist.near"
   }' --accountId attacker.near
   ```
   Because `new()` never checks `env::state_exists()` [6](#0-5) , this call succeeds and overwrites `owner_account_id` to `attacker.near`.
3. Attacker now calls owner-gated methods (e.g., in `owner.rs`) such as those wrapping deposit/unstake/withdraw/transfer, passing `assert_owner()` since `self.owner_account_id == predecessor` now: [7](#0-6) 
4. Attacker drains the contract's NEAR balance to their own account.

### Citations

**File:** lockup-factory/src/lib.rs (L75-80)
```rust
    #[init]
    pub fn new(
        whitelist_account_id: ValidAccountId,
        foundation_account_id: ValidAccountId,
    ) -> Self {
        assert!(!env::state_exists(), "The contract is already initialized");
```

**File:** lockup-factory/src/lib.rs (L107-157)
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
```

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

**File:** lockup/src/owner.rs (L12-13)
```rust
    pub fn select_staking_pool(&mut self, staking_pool_account_id: AccountId) -> Promise {
        self.assert_owner();
```

**File:** lockup/src/owner.rs (L49-52)
```rust
    pub fn unselect_staking_pool(&mut self) {
        self.assert_owner();
        self.assert_staking_pool_is_idle();
        self.assert_no_termination();
```
