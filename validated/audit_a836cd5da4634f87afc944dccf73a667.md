## Analog Found

### Title
Lockup contract `new` (init) function lacks reinitialization guard, allowing unprivileged takeover of locked funds - (File: `lockup/src/lib.rs`)

### Summary
The `lockup` contract's `#[init]` function `LockupContract::new` never checks `env::state_exists()` before overwriting the contract's state, unlike every sibling contract in this repository (`multisig`, `staking-pool`, `whitelist`, `lockup-factory`), which all explicitly guard their `new` with `assert!(!env::state_exists(), "Already initialized")`. This is the exact root cause class described in the external CoreCollection report: a public initializer that can be re-run to reset core state.

### Finding Description
`LockupContract::new` at [1](#0-0)  builds and returns a fresh `Self` struct containing `owner_account_id`, `lockup_information`, `vesting_information`, `staking_pool_whitelist_account_id`, `staking_information`, and `foundation_account_id` — with no check that the contract has already been initialized. Compare this to the other contracts in the same repo which all defend against reinitialization:
- `multisig/src/lib.rs`: `assert!(!env::state_exists(), "Already initialized");` [2](#0-1) 
- `staking-pool/src/lib.rs`: `assert!(!env::state_exists(), "Already initialized");` [3](#0-2) 
- `whitelist/src/lib.rs`: `assert!(!env::state_exists(), "Already initialized");` [4](#0-3) 
- `lockup-factory/src/lib.rs`: `assert!(!env::state_exists(), "The contract is already initialized");` [5](#0-4) 

`new` is a plain public method (not owner-gated — it can't be, since it establishes the owner), so any unprivileged account can call it against an already-deployed and funded lockup contract at any time, since NEAR's `#[init]` attribute in this SDK version does not itself enforce single-execution — that responsibility is left to the developer, as evidenced by the other four contracts implementing the check manually.

An attacker can call `new` on the live lockup account with attacker-chosen parameters: `owner_account_id = <attacker>`, `transfers_information = TransfersEnabled { transfers_timestamp: 0 }`, `vesting_schedule = None`, `foundation_account_id = None`, `release_duration = None`/minimal. This resets `owner_account_id` to the attacker and clears vesting/termination controls, while `lockup_information.lockup_amount` is recomputed from `env::account_balance()` (the current, already-funded balance).

Once `owner_account_id` is attacker-controlled, all owner-gated methods in `lockup/src/owner.rs` (guarded only by `self.assert_owner()`, e.g. at [6](#0-5) ) become callable by the attacker, including the transfer/withdraw methods that move liquid NEAR out of the contract to the (now attacker) owner account.

### Impact Explanation
This is a Critical impact under the allowed scope: "Unauthorized transfer, withdrawal, spending, or release of locked, vested, pooled ... NEAR through public-call ... failure reachable by an unprivileged user," and also "Permanent freezing/irrevocable loss of user or protocol funds in lockup release ... flows." An unprivileged attacker can re-run `new` on any deployed `LockupContract`, seize the `owner_account_id` role, strip vesting/foundation-termination protections, and then withdraw the full locked NEAR balance via the owner-only transfer path.

### Likelihood Explanation
Likelihood is high: `new` is a normal public contract method with no owner check (by necessity, since it sets the owner), requires no special privilege, key, or race condition — a single unprivileged `near call <lockup_account> new '{...attacker params...}'` transaction executed at any point after the legitimate initial deployment is sufficient.

### Recommendation
Add the same reinitialization guard used elsewhere in this codebase to `LockupContract::new`:
```rust
#[init]
pub fn new(...) -> Self {
    assert!(!env::state_exists(), "The contract is already initialized");
    ...
}
```

### Proof of Concept
1. `near_account` deploys and initializes `lockup1` legitimately via `new(...)` with `owner_account_id = owner1`, funded with locked NEAR.
2. Attacker (any unprivileged account) calls:
```bash
near call lockup1 new '{
  "owner_account_id": "attacker.near",
  "lockup_duration": "0",
  "lockup_timestamp": null,
  "transfers_information": { "TransfersEnabled": { "transfers_timestamp": "0" } },
  "vesting_schedule": null,
  "release_duration": null,
  "staking_pool_whitelist_account_id": "staking-pool-whitelist",
  "foundation_account_id": null
}' --accountId=attacker.near
```
Because `lockup/src/lib.rs` `new` ( [1](#0-0) ) never checks `env::state_exists()`, this call succeeds and resets `owner_account_id` to `attacker.near`, with transfers already enabled and no vesting/foundation restriction.
3. Attacker then calls owner-only withdrawal/transfer methods in `lockup/src/owner.rs` (protected only by `self.assert_owner()`, e.g. [6](#0-5) ), now succeeding since `self.owner_account_id == attacker.near`, draining the locked NEAR balance.

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

**File:** lockup/src/owner.rs (L12-13)
```rust
    pub fn select_staking_pool(&mut self, staking_pool_account_id: AccountId) -> Promise {
        self.assert_owner();
```
