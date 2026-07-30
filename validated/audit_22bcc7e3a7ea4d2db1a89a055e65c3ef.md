### Title
Missing re-initialization guard in `LockupContract::new()` allows hijacking of an already-funded lockup - (File: lockup/src/lib.rs)

### Summary
The `lockup/src/lib.rs` `LockupContract::new()` `#[init]` constructor does not verify `env::state_exists()` before running, unlike every other `#[init]` constructor in the in-scope contracts (`whitelist/src/lib.rs`, `staking-pool/src/lib.rs`, `staking-pool-factory/src/lib.rs`, `multisig/src/lib.rs`), all of which explicitly assert `!env::state_exists()` to prevent re-initialization. This is the same root-cause class as the reported `initAuctionLauncher()` issue: an initializer function that is reachable without checking whether the contract has already been (or should already be) initialized, letting an unprivileged caller set themselves up as a privileged party.

### Finding Description
`LockupContract::new()` is marked `#[init]` but performs no `assert!(!env::state_exists(), ...)` check before writing the new contract state: [1](#0-0) 

Compare this with the sibling contracts in the same audit scope, which all defensively guard their initializer against being called more than once: [2](#0-1) [3](#0-2) [4](#0-3) 

Because the lockup contract holds real, already-transferred NEAR tokens by the time `new()` is expected to be called (deployment and funding typically precede/accompany initialization, e.g. via `lockup-factory`), and because `new()` recomputes `lockup_amount: env::account_balance()` and freely sets `owner_account_id`, `vesting_information`, `staking_pool_whitelist_account_id`, and `foundation_account_id` from caller-supplied arguments every time it is invoked, any account able to call the `new` method on that lockup account can:
- Front-run the legitimate initialization transaction if deployment and initialization happen as separate transactions, setting themselves as `owner_account_id` before the rightful owner initializes.
- Or, if the contract account's access keys are not fully removed/locked down after legitimate initialization, re-invoke `new()` at any later point to overwrite the owner and vesting/termination configuration, effectively seizing control of the funds already locked in the account.

This mirrors the reported class of bug: an initializer with no restriction on who/when it can be called, enabling privilege takeover.

### Impact Explanation
This maps to the "Critical — Unauthorized transfer, withdrawal, spending, or release of locked... NEAR" and "Critical — Permanent freezing... or irrevocable loss of user or protocol funds in lockup release... flows" impact categories. If `new()` can be invoked after the contract already holds locked NEAR (a race during deployment, or any surviving access key on the lockup account), an attacker can overwrite `owner_account_id` and vesting/foundation configuration and gain control over the already-funded lockup balance, up to withdrawing the locked NEAR to themselves once transfers are enabled/owner-controlled flows are exercised.

### Likelihood Explanation
Likelihood depends on the deployment workflow: if account creation, contract deployment, funding, and the `new()` call are not atomically bundled in a single transaction (batch of actions), there is a window during which any account can call `new()` on the freshly-created, not-yet-initialized (but possibly already funded) lockup account before the legitimate initializer does. This is a realistic risk in decoupled/manual deployment flows and is exactly the class of race the report's recommendation ("only the deployer should call init") is meant to close. It is comparable in nature, though not identical in exploitation mechanics, to the analogous fix already applied to `whitelist`, `staking-pool`, `staking-pool-factory`, and `multisig` in this same codebase, all of which explicitly guard against re-invocation with `state_exists()`.

### Recommendation
Add `assert!(!env::state_exists(), "The contract is already initialized");` as the first line of `LockupContract::new()` in `lockup/src/lib.rs`, consistent with the pattern already used in `whitelist/src/lib.rs`, `staking-pool-factory/src/lib.rs`, and `multisig/src/lib.rs`. Additionally, ensure deployment tooling (e.g., `lockup-factory`) always bundles account creation, contract deployment, funding, and the `new()` call into a single atomic transaction so no window exists for a front-running `new()` call.

### Proof of Concept
1. An account is created and the lockup contract binary is deployed to it, but the transaction that calls `new(...)` to initialize it is submitted separately (e.g., due to tooling limits or manual multi-step deployment).
2. Before the legitimate deployer's `new()` transaction lands, an unprivileged attacker submits their own `new()` call to the same lockup account with `owner_account_id` set to their own account and no restrictive vesting schedule.
3. Because `LockupContract::new()` (lockup/src/lib.rs:180-243) never checks `env::state_exists()`, the call succeeds and sets the attacker as `owner_account_id` of the LockupContract state, using `env::account_balance()` (which may already include NEAR sent to the account) as `lockup_amount`.
4. The attacker, now recorded as owner, can subsequently exercise owner-only withdrawal/transfer functionality against the locked balance.

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

**File:** whitelist/src/lib.rs (L32-44)
```rust
    #[init]
    pub fn new(foundation_account_id: AccountId) -> Self {
        assert!(!env::state_exists(), "Already initialized");
        assert!(
            env::is_valid_account_id(foundation_account_id.as_bytes()),
            "The NEAR Foundation account ID is invalid"
        );
        Self {
            foundation_account_id,
            whitelist: LookupSet::new(b"w".to_vec()),
            factory_whitelist: LookupSet::new(b"f".to_vec()),
        }
    }
```

**File:** staking-pool-factory/src/lib.rs (L104-115)
```rust
    #[init]
    pub fn new(staking_pool_whitelist_account_id: AccountId) -> Self {
        assert!(!env::state_exists(), "The contract is already initialized");
        assert!(
            env::is_valid_account_id(staking_pool_whitelist_account_id.as_bytes()),
            "The staking pool whitelist account ID is invalid"
        );
        Self {
            staking_pool_whitelist_account_id,
            staking_pool_account_ids: UnorderedSet::new(b"s".to_vec()),
        }
    }
```

**File:** multisig/src/lib.rs (L102-113)
```rust
    #[init]
    pub fn new(num_confirmations: u32) -> Self {
        assert!(!env::state_exists(), "Already initialized");
        Self {
            num_confirmations,
            request_nonce: 0,
            requests: UnorderedMap::new(b"r".to_vec()),
            confirmations: UnorderedMap::new(b"c".to_vec()),
            num_requests_pk: UnorderedMap::new(b"k".to_vec()),
            active_requests_limit: 12,
        }
    }
```
