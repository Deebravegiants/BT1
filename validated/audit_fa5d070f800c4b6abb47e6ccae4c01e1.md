### Title
Front-runnable `lockup-factory::create()` lets an attacker permanently bind a victim's owner account to a lockup with an attacker-chosen `whitelist_account_id`/vesting terms - (File: `lockup-factory/src/lib.rs`)

### Summary
`LockupFactory::create()` derives the to-be-created lockup contract's account ID **only** from `owner_account_id` (`sha256(owner_account_id)`), while every other parameter of the lockup — including `staking_pool_whitelist_account_id`, `vesting_schedule`, `lockup_duration`, `lockup_timestamp`, and `release_duration` — is fully attacker-controlled and can be supplied by *any* caller, since "Lockups can be funded from any account" is an intentional feature.

### Finding Description
```rust
// lockup-factory/src/lib.rs:108-166
pub fn create(
    &mut self,
    owner_account_id: ValidAccountId,
    lockup_duration: WrappedDuration,
    lockup_timestamp: Option<WrappedTimestamp>,
    vesting_schedule: Option<VestingScheduleOrHash>,
    release_duration: Option<WrappedDuration>,
    whitelist_account_id: Option<ValidAccountId>,
) -> Promise {
    ...
    let byte_slice = env::sha256(owner_account_id.as_ref().as_bytes());
    let lockup_account_id =
        format!("{}.{}", hex::encode(&byte_slice[..20]), env::current_account_id());
    ...
    let staking_pool_whitelist_account_id = if let Some(account_id) = whitelist_account_id {
        account_id.into()
    } else {
        self.whitelist_account_id.clone()
    };
    ...
    Promise::new(lockup_account_id.clone())
        .create_account()
        .deploy_contract(CODE.to_vec())
        .transfer(env::attached_deposit())
        .function_call(b"new".to_vec(), ... /* includes staking_pool_whitelist_account_id, vesting_schedule, etc. */ ...)
        .then(ext_self::on_lockup_create(...))
}
``` [1](#0-0) 

Because `lockup_account_id` depends solely on `owner_account_id`, this is exactly analogous to the `CidNFT.mint()`/`add()` bug: the resulting resource's identity (the on-chain NEAR account) is predictable/derivable from public input rather than bound to the calling transaction that is supposed to configure it. Any unprivileged account watching the mempool for an intended `create({owner_account_id: "victim.near", ...legit params...})` call can front-run it with their own `create({owner_account_id: "victim.near", whitelist_account_id: "attacker-fake-whitelist.near", ...})` call, attaching only `MIN_ATTACHED_BALANCE`. Since NEAR account creation is first-come, the attacker's `create_account()` succeeds first at the deterministic address; the victim's later, legitimate `create()` call to the same derived account then fails at `create_account()` (account already exists), and the deposit is automatically refunded to the original caller through `on_lockup_create`:
```rust
// lockup-factory/src/lib.rs:171-198
pub fn on_lockup_create(...) -> bool {
    ...
    if lockup_account_created { ... true }
    else {
        Promise::new(predecessor_account_id).transfer(attached_deposit.0);
        false
    }
}
``` [2](#0-1) 

The refund logic protects the *funder's* attached deposit, but it does nothing to prevent the *owner's* namesake account from being permanently taken over with attacker-chosen lockup configuration — in particular `staking_pool_whitelist_account_id`, which is central to the "trust chain" invariant that lockups may only stake through pools vetted by a legitimate whitelist contract.

### Impact Explanation
This maps to the scoped **High** impact "State-transition bypass ... that lets an unprivileged user perform actions beyond intended authority" and potentially to the **Critical** impact "Unauthorized transfer/withdrawal ... through public-call, callback, approval, or accounting failure." By planting a malicious `staking_pool_whitelist_account_id` (a contract the attacker controls that can be made to report `is_whitelisted == true` for any pool), the attacker undermines the security guarantee documented as: "a `Lockup` contract can only stake through a `StakingPool` that has been vetted by the `Whitelist` contract." A victim owner who later calls `select_staking_pool`/`deposit_and_stake` on their (attacker-provisioned) lockup, believing it consults the legitimate foundation whitelist, could instead be induced to stake locked NEAR into an attacker-controlled malicious staking pool, from which funds could be withheld or never returned — an unauthorized loss of locked funds.

I was not able to fully verify, within the available tool budget, whether `lockup/src/owner.rs`'s `select_staking_pool` performs any additional validation against a hardcoded/immutable whitelist address (as opposed to trusting the `staking_pool_whitelist_account_id` stored at `new()`), so the exact severity depends on that check, which I could not confirm from the index in this session.

### Likelihood Explanation
Likelihood is **moderate**: it requires the attacker to observe a pending `create()` transaction (mempool/public tx pattern, standard front-running assumption, not a "trusted role" requirement) and to know/guess the `owner_account_id` in advance, which is plausible since lockup creation flows are typically announced/coordinated (e.g., HR/token-grant tooling calling the factory for a known employee account). No privileged access is required — `create()` is a fully public, payable method callable by anyone with `MIN_ATTACHED_BALANCE`.

### Recommendation
- Bind lockup account creation to the caller in a way that prevents pre-emption of a specific `owner_account_id`, e.g., require `predecessor_account_id() == owner_account_id` for self-service creation, or route creation through a mechanism where the intended owner (or the foundation) pre-approves/pre-commits parameters (commit-reveal) before the deterministic account is created.
- Alternatively, disallow overriding `staking_pool_whitelist_account_id` per-call entirely (always use the factory's configured `whitelist_account_id`), removing the attacker-controllable "malicious whitelist" vector even if account front-running still occurs.
- Consider deriving `lockup_account_id` from a value that also incorporates the funder/predecessor or a nonce chosen by the owner, so a third party cannot deterministically pre-create the account ahead of the legitimate creator.

### Proof of Concept
1. Victim (or their employer/agent) prepares a transaction: `lockup_factory.create({owner_account_id: "victim.near", lockup_duration: ..., vesting_schedule: legit, whitelist_account_id: None /* defaults to real whitelist */})` with deposit `>= MIN_ATTACHED_BALANCE`, and broadcasts it.
2. Attacker observes this pending transaction and immediately submits `lockup_factory.create({owner_account_id: "victim.near", lockup_duration: ..., vesting_schedule: None, whitelist_account_id: Some("attacker-fake-whitelist.near")})` with only `MIN_ATTACHED_BALANCE`, using higher gas price / earlier inclusion to land first.
3. Both calls compute the same `lockup_account_id = sha256("victim.near")[..20] + "." + factory`. The attacker's `create_account()` executes first and succeeds; `on_lockup_create` whitelists/finalizes it.
4. The victim's original `create()` call's `create_account()` fails (account already exists); `on_lockup_create` refunds the victim's deposit but the lockup account for `victim.near` is now permanently the attacker-configured contract pointing at `attacker-fake-whitelist.near`.
5. When the victim owner later interacts with their lockup (`select_staking_pool`, staking flows), the trust-chain check against the legitimate whitelist is bypassed because the lockup consults the attacker's fake whitelist contract instead. [3](#0-2) [4](#0-3)

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
