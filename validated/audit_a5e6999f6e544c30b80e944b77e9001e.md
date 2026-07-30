### Title
Front-runnable, permissionless lockup creation lets an attacker permanently squat a beneficiary's deterministic lockup account with attacker-chosen terms - (File: lockup-factory/src/lib.rs)

### Summary
`LockupFactory::create` derives the new lockup contract's account ID **deterministically** from only the `owner_account_id` argument (`sha256(owner_account_id)` truncated + factory account), and the function is public/permissionless with no reservation or authorization check tying the call to the intended (e.g. foundation) caller. Any unprivileged account can call `create` first for a target `owner_account_id`, claiming that exact deterministic address with attacker-chosen `lockup_duration`, `lockup_timestamp`, `vesting_schedule`, and `whitelist_account_id`. This is the same root-cause class as the reported Sui `validate_and_store_payload` issue: a public function that permanently consumes a unique identifier/slot before the legitimate caller's transaction lands, causing the legitimate transaction to fail and blocking the intended, correctly-configured effect.

### Finding Description
`create()` computes the lockup account deterministically: [1](#0-0) 
and then unconditionally issues `Promise::new(lockup_account_id).create_account()...` with no check that the caller is authorized for this `owner_account_id`, and no reservation/registry check beyond NEAR's own "account already exists" failure semantics: [2](#0-1) 

Because the account name depends only on `owner_account_id` (a value fully known/public once chosen, e.g. an employee or investor address), any unprivileged third party can call `create(owner_account_id, ...)` with their own attached deposit (≥ `MIN_ATTACHED_BALANCE`) before the legitimate, properly-parameterized call (e.g. from the foundation account) executes. Since NEAR sub-account creation is a one-time, irreversible operation, whichever call reaches the network first "wins" the account name permanently. The attacker fully controls `lockup_duration`, `lockup_timestamp`, `vesting_schedule`, `release_duration`, and `staking_pool_whitelist_account_id` for that squatted contract, while `owner_account_id` remains the intended victim's account (so the attacker cannot steal the funds directly, but can force an arbitrary, incorrect lockup/vesting configuration onto that identifier and block the real one from ever being created).

The legitimate caller's subsequent `create()` call will fail at `create_account()` (the account already exists), triggering the refund path in `on_lockup_create`: [3](#0-2) 
so the legitimate caller's deposit is refunded, but the deterministic lockup address for that `owner_account_id` is now permanently occupied by an attacker-defined (non-vesting, non-foundation-controlled, or otherwise malformed) lockup contract — this is an irrevocable state-transition bypass on a public, unprivileged entrypoint.

### Impact Explanation
This matches the report class "High: State-transition bypass in lockup flows that lets an unprivileged user perform actions beyond intended authority," because an unprivileged attacker can dictate the lockup/vesting terms deployed at the one-and-only deterministic account address reserved for a specific beneficiary, permanently preempting the foundation's ability to deploy the intended, correctly configured lockup contract for that account. Because NEAR account creation is irreversible, this is not a transient griefing but a permanent denial of the correct lockup/vesting setup for the targeted beneficiary — bordering on the "Critical: permanent freezing/irrevocable loss ... in lockup release ... flows" category if the intended vesting/lockup for that beneficiary can never subsequently be established at any other address expected by off-chain tooling/UI that assumes the deterministic address.

### Likelihood Explanation
Exploitation only requires knowledge of a target `owner_account_id` (which is typically public/known in advance, e.g. published team/investor account IDs) and the ability to submit a public transaction with sufficient attached NEAR (`MIN_ATTACHED_BALANCE`, 3.5 NEAR) before the legitimate creator's transaction is included — a straightforward front-run given NEAR's public mempool/transaction visibility. No privileged role, key, or trusted contract is required; the attacker only spends their own NEAR (paid as the contract's initial balance), making this a realistic, low-cost griefing vector for anyone who wants to block or corrupt a specific beneficiary's lockup deployment.

### Recommendation
- Restrict who may call `create()` for a given `owner_account_id` (e.g., require `predecessor_account_id() == foundation_account_id` or another authorized/whitelisted caller), or
- Make the lockup account name non-deterministic / caller-chosen with an explicit collision check registry (similar to `staking-pool-factory`'s `staking_pool_account_ids` set) combined with an authorization check, or
- Have the factory maintain an on-chain reservation/allow-list per `owner_account_id` before allowing account creation, so an unprivileged party cannot preempt a specific beneficiary's deterministic address.

### Proof of Concept
1. Attacker observes/knows `owner_account_id = "victim.near"` is scheduled to receive a foundation-managed lockup with vesting.
2. Attacker (unprivileged) calls `lockup_factory.create(owner_account_id="victim.near", lockup_duration=0, lockup_timestamp=None, vesting_schedule=None, release_duration=None, whitelist_account_id=None)` with `MIN_ATTACHED_BALANCE` NEAR attached, before the foundation's intended transaction is processed. [4](#0-3) 
3. NEAR creates the sub-account `sha256("victim.near")[..20 hex].lockup_factory.near` and deploys/initializes it with the attacker's chosen (non-vesting, zero-duration) lockup parameters, owned by `victim.near`.
4. The foundation's later call to `create()` with the correct vesting/lockup parameters for `"victim.near"` fails because the account already exists; the foundation's deposit is refunded via `on_lockup_create`, but the deterministic lockup address for `"victim.near"` now permanently contains the attacker-defined, incorrect lockup contract instead of the intended vesting lockup. [3](#0-2) 

*(Note: this analysis is scoped to `lockup-factory/src/lib.rs` as the closest reachable analog of the reported class in the requested production files; I did not find an equivalent unauthorized "mark-as-used/front-run" pattern reachable by a strictly unprivileged attacker in `lockup/src`, `staking-pool/src`, `whitelist/src`, or `multisig/src` — the closest other candidate, `staking-pool-factory::create_staking_pool`, requires the attacker to guess the victim's chosen `staking_pool_id` string rather than a value derivable from public information, making it less directly analogous.)*

### Citations

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

**File:** lockup-factory/src/lib.rs (L171-198)
```rust
    pub fn on_lockup_create(
        &mut self,
        lockup_account_id: AccountId,
        attached_deposit: U128,
        predecessor_account_id: AccountId,
    ) -> bool {
        assert_self();

        let lockup_account_created = is_promise_success();

        if lockup_account_created {
            env::log(
                format!("The lockup contract {} was successfully created.", lockup_account_id)
                    .as_bytes(),
            );
            true
        } else {
            env::log(
                format!(
                    "The lockup {} creation has failed. Returning attached deposit of {} to {}",
                    lockup_account_id, attached_deposit.0, predecessor_account_id
                )
                    .as_bytes(),
            );
            Promise::new(predecessor_account_id).transfer(attached_deposit.0);
            false
        }
    }
```
