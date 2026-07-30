### Title
Frontrunnable `new` initializer allows unauthorized takeover of a funded but uninitialized `LockupContract` - (File: `lockup/src/lib.rs`)

### Summary
The external report describes Algebra's `initialize()` function as an unprotected, single-shot state-setting entrypoint that any address can call once — allowing an attacker to race ("frontrun") the legitimate caller and control the critical initial state. `core-contracts` has the exact same root-cause pattern in every contract's `#[init] pub fn new(...)`, and the impact is materially worse for `lockup/src/lib.rs` because the account already holds real, transferred NEAR balance at the moment `new` becomes callable.

### Finding Description
`LockupContract::new` is guarded only by `assert!(!env::state_exists(), "The contract is not initialized...")` — there is no check that `env::predecessor_account_id()` is the deployer, the foundation, or any other authorized identity: [1](#0-0) 

Deployment of a lockup contract is documented and normally executed as **two separate transactions**: first the account is created and funded and the contract binary is deployed (which transfers the locked NEAR balance onto the account), and only afterward is `new(...)` invoked as a distinct `near call lockup1 new ...` transaction: [2](#0-1) 

Because these are two independent, publicly broadcast transactions, an unprivileged attacker monitoring the mempool can submit their own `new(...)` call with attacker-controlled `owner_account_id` and land it before the legitimate initialization transaction. `new()` unconditionally sets `lockup_information.lockup_amount = env::account_balance()` (i.e., whatever NEAR has already been deposited on the account) and stores the attacker as `owner_account_id`: [3](#0-2) 

Since `env::state_exists()` becomes true after the first successful `new()` call, the legitimate owner's subsequent `new()` transaction reverts with `"Already initialized"`, permanently locking the legitimate owner out. All owner-privileged methods gate on `assert_owner()`, which now matches the attacker's account: [4](#0-3) 

The same missing-caller-authorization pattern exists in the other production contracts' initializers (`staking-pool/src/lib.rs`, `staking-pool-factory/src/lib.rs`, `whitelist/src/lib.rs`, `multisig/src/lib.rs`), all of which check only `!env::state_exists()`: [5](#0-4) [6](#0-5) 

However `staking-pool-factory`'s `create_staking_pool` bundles `create_account`, `transfer`, `deploy_contract`, and `function_call("new", ...)` into a single atomic Promise batch executed as one receipt, so that path is not exploitable this way: [7](#0-6) 

`lockup/src/lib.rs` is the highest-impact instance because it is the contract most commonly deployed via the manual two-step flow with real NEAR balance already present before `new()` executes.

### Impact Explanation
If an attacker's `new()` call lands first, the attacker becomes `owner_account_id` of an account that already holds the intended locked NEAR balance. Depending on the `vesting_schedule`/`transfers_information` the legitimate deployer intended to set, the attacker instead controls those parameters and can potentially call `transfer` (if they set transfers already enabled and no vesting), `select_staking_pool` + `deposit_and_stake` to redirect funds to a pool they control, or `add_full_access_key` once locked funds are released — resulting in unauthorized transfer/withdrawal of NEAR that was meant to be locked for the true owner, or at minimum permanent loss of control (irrecoverable takeover) of the lockup account for its rightful owner, since re-initialization is blocked once state exists. This matches the Critical impact categories for "unauthorized transfer... of locked... NEAR through public-call... accounting failure" and "permanent freezing/irrevocable loss of user... funds in lockup release... flows."

### Likelihood Explanation
Exploitation requires only that the attacker observe the lockup account being created/funded and its `new()` call broadcast to the mempool as a separate transaction — exactly the deployment flow documented in `lockup/README.md`. No privileged role, signing key, or trusted position is needed; this mirrors the exact frontrunning mechanics described in the source report (mempool-listening bot racing a public, unauthenticated single-shot initializer).

### Recommendation
Restrict `new()`/`#[init]` calls to only be executable by an authorized predecessor (e.g., require `env::predecessor_account_id() == env::current_account_id()`, meaning it can only be self-called as part of the same deploy transaction/batch, as the factory already does atomically), or require deployment and initialization to be bundled into a single atomic transaction (multiple actions in one `near` transaction, as shown in `scripts/deploy/deploy_staking_pool_factory.sh`) rather than documenting/allowing a two-step deploy-then-`near call new` flow.

### Proof of Concept
1. Deployer creates account `lockup1`, transfers the intended locked NEAR amount, and deploys the lockup contract binary to it (transaction 1).
2. Deployer broadcasts transaction 2: `near call lockup1 new '{"owner_account_id": "owner1", ...}' --accountId=near`.
3. Attacker monitors the mempool for a `new` function call targeting `lockup1` (function signature match, analogous to the report's `mempool.js` snippet watching for `0xf637731d`).
4. Attacker submits their own `near call lockup1 new '{"owner_account_id": "attacker", ...}'` with higher gas price/priority so it lands first.
5. `LockupContract::new` at `lockup/src/lib.rs:180-243` succeeds since `env::state_exists()` is still false, setting `owner_account_id = attacker` and `lockup_information.lockup_amount = env::account_balance()` (the already-transferred funds).
6. Deployer's original transaction 2 now reverts with `"The contract is not initialized."`/state-exists assertion, permanently leaving `attacker` as owner of `lockup1` holding the deposited NEAR.

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

**File:** lockup/README.md (L137-178)
```markdown
### Initialization

Initialize contract, assuming it's called from `near` account.
The lockup contract account ID is `lockup1`.
The owner account ID is `owner1`.
Lockup Duration is 365 days, starting from `2018-09-01` (`lockup_timestamp` and `release_duration` args).
Release duration is 4 years (or 1461 days including leap year).
Transfers are enabled `2020-10-13`.
Vesting is 4 years starting from `2018-09-01` to `2022-09-01` Pacific time.
Staking pool whitelist contract is at `staking-pool-whitelist`.
The foundation account ID that can terminate vesting is `near`.

Arguments in JSON format

```json
{
    "owner_account_id": "owner1",
    "lockup_duration": "0",
    "lockup_timestamp": "1535760000000000000",
    "release_duration": "126230400000000000",
    "transfers_information": {
        "TransfersEnabled": {
            "transfers_timestamp": "1602614338293769340"
        }
    },
    "vesting_schedule": {
        "VestingSchedule": {
            "start_timestamp": "1535760000000000000",
            "cliff_timestamp": "1567296000000000000",
            "end_timestamp": "1661990400000000000"
        }
    },
    "staking_pool_whitelist_account_id": "staking-pool-whitelist",
    "foundation_account_id": "near"
}
```

Command

```bash
near call lockup1 new '{"owner_account_id": "owner1", "lockup_duration": "0", "lockup_timestamp": "1535760000000000000", "release_duration": "126230400000000000", "transfers_information": {"TransfersEnabled": {"transfers_timestamp": "1602614338293769340"}}, "vesting_schedule": {"VestingSchedule": {"start_timestamp": "1535760000000000000", "cliff_timestamp": "1567296000000000000", "end_timestamp": "1661990400000000000"}}, "staking_pool_whitelist_account_id": "staking-pool-whitelist", "foundation_account_id": "near"}' --accountId=near --gas=25000000000000
```
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

**File:** staking-pool-factory/src/lib.rs (L172-195)
```rust
        Promise::new(staking_pool_account_id.clone())
            .create_account()
            .transfer(env::attached_deposit())
            .deploy_contract(include_bytes!("../../staking-pool/res/staking_pool.wasm").to_vec())
            .function_call(
                b"new".to_vec(),
                near_sdk::serde_json::to_vec(&StakingPoolArgs {
                    owner_id,
                    stake_public_key,
                    reward_fee_fraction,
                })
                .unwrap(),
                NO_DEPOSIT,
                gas::STAKING_POOL_NEW,
            )
            .then(ext_self::on_staking_pool_create(
                staking_pool_account_id,
                env::attached_deposit().into(),
                env::predecessor_account_id(),
                &env::current_account_id(),
                NO_DEPOSIT,
                gas::CALLBACK,
            ))
    }
```
