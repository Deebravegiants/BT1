### Title
Missing re-initialization guard in `LockupContract::new` allows contract takeover and fund theft - (File: `lockup/src/lib.rs`)

### Summary
The external report's root cause class is "initializer callable multiple times / lacking a once-only guard," which allowed duplicate state to be added in `ManagedIndex.sol`. In `core-contracts`, every other production initializer explicitly protects against re-initialization with `assert!(!env::state_exists(), ...)`: `multisig/src/lib.rs` [1](#0-0) , `staking-pool/src/lib.rs` [2](#0-1) , `whitelist/src/lib.rs` [3](#0-2) , `lockup-factory/src/lib.rs` [4](#0-3) , and `staking-pool-factory/src/lib.rs`. However, `lockup/src/lib.rs`'s `LockupContract::new` — the main lockup contract holding user/locked/vested NEAR — has no such check.

### Finding Description
`LockupContract::new` is marked `#[init]` but performs only argument-validity assertions (valid account IDs, transfer-poll validity, vesting/foundation-account consistency); it never checks `env::state_exists()` before overwriting `self` [5](#0-4) . In this codebase's near-sdk version, the `#[init]` macro does not itself enforce single-call semantics — this is proven by the fact that every sibling contract (`multisig`, `staking-pool`, `whitelist`, `voting`, `lockup-factory`) has to add the `!env::state_exists()` assertion manually to prevent re-initialization. Because `new` is a normal public contract method with no owner/factory access control and no state guard, once a lockup contract account is deployed and initialized, any unprivileged caller can invoke `new` again on that same account and fully overwrite `owner_account_id`, `lockup_information`, `vesting_information`, `staking_information`, and `foundation_account_id`.

### Impact Explanation
By calling `new` a second time with `owner_account_id` set to their own account, an attacker becomes the recognized owner of the lockup contract. All owner-gated methods (e.g., transfer, select/unselect staking pool, stake, unstake, withdraw from staking pool) authorize solely by comparing `predecessor_account_id` to `self.owner_account_id`. After the takeover, the attacker can drain the locked/vested NEAR balance held by the contract through these owner methods — this is a Critical unauthorized withdrawal of locked funds via a public-call accounting/authorization failure reachable by an unprivileged user.

### Likelihood Explanation
Likelihood is high: `new` is a plain public function with no privileged-caller check and no re-init guard, directly reachable by any account with no special permission, and the exploit requires only a single function call with attacker-chosen parameters.

### Recommendation
Add `assert!(!env::state_exists(), "Already initialized");` at the start of `LockupContract::new` in `lockup/src/lib.rs`, consistent with the pattern already used in `multisig/src/lib.rs`, `staking-pool/src/lib.rs`, `whitelist/src/lib.rs`, and `lockup-factory/src/lib.rs`.

### Proof of Concept
1. Lockup contract account `lockup1` is deployed and initialized normally with `owner_account_id = "owner1"` via `new(...)`.
2. Attacker (any unprivileged account) calls:
   `near call lockup1 new '{"owner_account_id": "attacker", "lockup_duration": "0", "transfers_information": {"TransfersEnabled": {"transfers_timestamp": "0"}}, "staking_pool_whitelist_account_id": "staking-pool-whitelist", "foundation_account_id": null}' --accountId attacker`
3. Since `new` has no `state_exists` check, this call succeeds and overwrites contract state, setting `owner_account_id = "attacker"`.
4. Attacker now calls owner-only methods (e.g., `transfer`) as `attacker`, which pass the `owner_account_id` check and allow withdrawal of the contract's locked NEAR balance. [5](#0-4)

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

**File:** whitelist/src/lib.rs (L32-34)
```rust
    #[init]
    pub fn new(foundation_account_id: AccountId) -> Self {
        assert!(!env::state_exists(), "Already initialized");
```

**File:** lockup-factory/src/lib.rs (L76-80)
```rust
    pub fn new(
        whitelist_account_id: ValidAccountId,
        foundation_account_id: ValidAccountId,
    ) -> Self {
        assert!(!env::state_exists(), "The contract is already initialized");
```

**File:** lockup/src/lib.rs (L180-220)
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
```
