### Title
Missing `VestingSchedule::assert_valid()` check in lockup-factory `create()` allows unprivileged users to permanently brick a lockup contract's fund accounting - (File: lockup-factory/src/lib.rs, lockup/src/getters.rs)

### Summary
The external report describes a DoS caused by insufficient validation of pricing parameters, which lets an attacker create state that causes a later view/computation call to revert, permanently blocking a legitimate flow. The NEAR core-contracts codebase has an analogous root cause: `lockup-factory`'s public `create()` entrypoint never validates the attacker-supplied `vesting_schedule` timestamps before deploying and initializing a lockup contract, even though a validation helper (`VestingSchedule::assert_valid`) already exists in the codebase but is never invoked for this flow.

### Finding Description
`lockup-factory::create()` is a fully public, unprivileged entrypoint that lets any account create and fund a lockup contract for an arbitrary `owner_account_id`, passing through an arbitrary `vesting_schedule` argument: [1](#0-0) 

`VestingSchedule` defines an `assert_valid()` helper that enforces `start_timestamp <= cliff_timestamp <= end_timestamp` and `start_timestamp < end_timestamp`: [2](#0-1) 

An identical helper exists on the lockup contract side: [3](#0-2) 

However, a repo-wide search for actual calls to `assert_valid()` shows it is only invoked in `staking-pool/src/lib.rs` and `staking-pool-factory/src/lib.rs` — it is **never called** in `lockup-factory/src/lib.rs`'s `create()` nor in `lockup/src/lib.rs`'s `new()` initializer. This means a `VestingSchedule` with `start_timestamp > end_timestamp` (or `cliff_timestamp` outside `[start, end]`) can be stored unchecked into a freshly created lockup contract.

The unchecked schedule is later consumed by `get_unvested_amount`, which performs raw `u64` subtraction of the timestamps before any range checking: [4](#0-3) 

If `start_timestamp > end_timestamp`, `vesting_schedule.end_timestamp.0 - vesting_schedule.start_timestamp.0` underflows. `get_unvested_amount` is called from `get_locked_amount`: [5](#0-4) 

`get_locked_amount`/`get_owners_balance`/`get_liquid_owners_balance` gate essentially all fund-moving owner operations (staking, transferring, adding a full access key). If the underflow panics (as is standard/expected when `overflow-checks` is enabled, which is the norm for financial NEAR contracts), every subsequent call into these getters — and therefore every owner action depending on them — reverts permanently.

### Impact Explanation
Because `lockup-factory::create()` is unprivileged and public, any attacker can:
1. Pass a malicious/invalid `vesting_schedule` (e.g., `start_timestamp` far larger than `end_timestamp`) for a chosen `owner_account_id`.
2. Since the lockup account address is deterministically derived from `sha256(owner_account_id)` [6](#0-5) , the attacker can front-run/pre-create a target's lockup account with a broken schedule before the legitimate owner does, permanently occupying that address and denying the intended owner the ability to ever set up a valid lockup, or
3. Deposit real funds (minimum required attached balance) into a lockup contract that is permanently broken from creation — any tokens later sent to that account become effectively unrecoverable since `get_locked_amount`/`get_owners_balance` (required by transfer/staking flows) will always panic.

This matches the "Critical: Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release ... flows" impact category, reachable entirely through the public, unprivileged `create()` call.

### Likelihood Explanation
Likelihood is high: the entrypoint is fully public and requires no special role — only the minimum attached deposit (3.5 NEAR) [7](#0-6) . No cooperation from the target owner is required, and the validation gap is a simple missing function call rather than a complex exploit, making it trivial to trigger with crafted `vesting_schedule` values.

### Recommendation
Call `vesting_schedule.assert_valid()` in `lockup-factory::create()` whenever a plain `VestingScheduleOrHash::VestingSchedule` variant is supplied, and also validate schedule invariants inside `lockup::new()` before persisting `vesting_information`, mirroring the pattern already used in `staking-pool` and `staking-pool-factory`. Additionally, replace raw arithmetic in `get_unvested_amount`/`get_locked_amount` with checked/saturating operations so a stored invalid schedule cannot cause an unrecoverable panic even as defense-in-depth.

### Proof of Concept
1. Attacker calls `lockup-factory.create` with:
   - `owner_account_id`: attacker-chosen victim or attacker's own address for later griefing/front-running,
   - `vesting_schedule: { VestingSchedule: { start_timestamp: <very large>, cliff_timestamp: <very large>, end_timestamp: <small> } }` (violates `start <= cliff <= end` and `start < end`).
2. `lockup-factory::create()` performs no validation (`lockup-factory/src/lib.rs:107-166`) and deploys+initializes the lockup contract with this schedule.
3. Any subsequent call to `get_locked_amount`, `get_owners_balance`, `get_liquid_owners_balance`, or any owner method depending on them (`select_staking_pool`, `deposit_and_stake`, `transfer`, `add_full_access_key`) triggers the underflow in `get_unvested_amount` at `lockup/src/getters.rs:140-143`, panicking and permanently reverting — freezing any funds held by that lockup account.

### Citations

**File:** lockup-factory/src/lib.rs (L34-34)
```rust
const MIN_ATTACHED_BALANCE: Balance = 3_500_000_000_000_000_000_000_000;
```

**File:** lockup-factory/src/lib.rs (L107-166)
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
            .then(ext_self::on_lockup_create(
                lockup_account_id,
                env::attached_deposit().into(),
                env::predecessor_account_id(),
                &env::current_account_id(),
                NO_DEPOSIT,
                gas::CALLBACK,
            ))
    }
```

**File:** lockup-factory/src/types.rs (L96-112)
```rust

impl VestingSchedule {
    pub fn assert_valid(&self) {
        assert!(
            self.start_timestamp.0 <= self.cliff_timestamp.0,
            "Cliff timestamp can't be earlier than vesting start timestamp"
        );
        assert!(
            self.cliff_timestamp.0 <= self.end_timestamp.0,
            "Cliff timestamp can't be later than vesting end timestamp"
        );
        assert!(
            self.start_timestamp.0 < self.end_timestamp.0,
            "The total vesting time should be positive"
        );
    }
}
```

**File:** lockup/src/types.rs (L110-125)
```rust
impl VestingSchedule {
    pub fn assert_valid(&self) {
        assert!(
            self.start_timestamp.0 <= self.cliff_timestamp.0,
            "Cliff timestamp can't be earlier than vesting start timestamp"
        );
        assert!(
            self.cliff_timestamp.0 <= self.end_timestamp.0,
            "Cliff timestamp can't be later than vesting end timestamp"
        );
        assert!(
            self.start_timestamp.0 < self.end_timestamp.0,
            "The total vesting time should be positive"
        );
    }
}
```

**File:** lockup/src/getters.rs (L64-113)
```rust
    /// Returns the amount of tokens that are locked in the account due to lockup or vesting.
    pub fn get_locked_amount(&self) -> WrappedBalance {
        let lockup_amount = self.lockup_information.lockup_amount;
        if let TransfersInformation::TransfersEnabled {
            transfers_timestamp,
        } = &self.lockup_information.transfers_information
        {
            let lockup_timestamp = std::cmp::max(
                transfers_timestamp
                    .0
                    .saturating_add(self.lockup_information.lockup_duration),
                self.lockup_information.lockup_timestamp.unwrap_or(0),
            );
            let block_timestamp = env::block_timestamp();
            if lockup_timestamp <= block_timestamp {
                let unreleased_amount =
                    if let &Some(release_duration) = &self.lockup_information.release_duration {
                        let end_timestamp = lockup_timestamp.saturating_add(release_duration);
                        if block_timestamp >= end_timestamp {
                            // Everything is released
                            0
                        } else {
                            let time_left = U256::from(end_timestamp - block_timestamp);
                            let unreleased_amount = U256::from(lockup_amount) * time_left
                                / U256::from(release_duration);
                            // The unreleased amount can't be larger than lockup_amount because the
                            // time_left is smaller than total_time.
                            unreleased_amount.as_u128()
                        }
                    } else {
                        0
                    };

                let unvested_amount = match &self.vesting_information {
                    VestingInformation::VestingSchedule(vs) => self.get_unvested_amount(vs.clone()),
                    VestingInformation::Terminating(terminating) => terminating.unvested_amount,
                    // Vesting is private, so we can assume the vesting started before lockup date.
                    _ => U128(0),
                };
                return std::cmp::max(
                    unreleased_amount
                        .saturating_sub(self.lockup_information.termination_withdrawn_tokens),
                    unvested_amount.0,
                )
                .into();
            }
        }
        // The entire balance is still locked before the lockup timestamp.
        (lockup_amount - self.lockup_information.termination_withdrawn_tokens).into()
    }
```

**File:** lockup/src/getters.rs (L138-149)
```rust
                } else {
                    // cannot overflow since block_timestamp < vesting_schedule.end_timestamp
                    let time_left = U256::from(vesting_schedule.end_timestamp.0 - block_timestamp);
                    // The total time is positive. Checked at the contract initialization.
                    let total_time = U256::from(
                        vesting_schedule.end_timestamp.0 - vesting_schedule.start_timestamp.0,
                    );
                    let unvested_amount = U256::from(lockup_amount) * time_left / total_time;
                    // The unvested amount can't be larger than lockup_amount because the
                    // time_left is smaller than total_time.
                    unvested_amount.as_u128().into()
                }
```
