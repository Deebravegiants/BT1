This confirms the mechanism: `select_staking_pool` in `lockup/src/owner.rs` checks the pool against `self.staking_pool_whitelist_account_id` via `ext_whitelist::is_whitelisted`, and this whitelist account ID is a field permanently fixed at contract initialization time (`LockupArgs::staking_pool_whitelist_account_id`), set from whatever `create()` caller supplied. [1](#0-0) 

### Title
Front-running account-name squatting in `LockupFactory::create` lets an attacker plant a malicious staking-pool whitelist for a victim's lockup account - (File: `lockup-factory/src/lib.rs`)

### Summary
`LockupFactory::create` is a public, unprivileged, payable entrypoint that deterministically derives the lockup contract's account ID solely from the hash of the caller-supplied `owner_account_id` [2](#0-1) . Because NEAR account IDs are globally unique and permanent once created, any unprivileged party — not just the intended `owner_account_id` or the NEAR Foundation — can call `create()` first for a victim's `owner_account_id`, permanently claiming that address and freely choosing all other initialization parameters, including `staking_pool_whitelist_account_id` [3](#0-2) .

### Finding Description
`create()` only requires `env::attached_deposit() >= MIN_ATTACHED_BALANCE` (3.5 NEAR) [4](#0-3) ; it does not require the caller to be the `owner_account_id`, the NEAR Foundation, or any privileged role. The resulting lockup account name is `sha256(owner_account_id)[..20] + "." + factory_account_id` [2](#0-1) , i.e. fully attacker-predictable and independent of who calls `create()`.

An attacker can front-run the legitimate lockup-creation transaction for a known/targeted `owner_account_id` (e.g. observed in the mempool, or simply predicted ahead of a publicized vesting grant), calling `create()` themselves with:
- `owner_account_id` = victim's account (so the deployed lockup's owner-gated methods remain callable by the victim — preserving the appearance of legitimacy),
- `staking_pool_whitelist_account_id` = a malicious whitelist contract fully controlled by the attacker (the parameter is entirely attacker-supplied and optional, defaulting only if omitted) [5](#0-4) ,
- minimal `vesting_schedule`/`release_duration` since the attacker only needs to win the account-name race, not fund the account.

Since NEAR account creation for an existing name fails, the legitimate creator's subsequent `create()` call for the same `owner_account_id` will fail and simply have its deposit refunded via the existing rollback path in `on_lockup_create` [6](#0-5)  — but the account name is now permanently squatted with attacker-chosen parameters. The `staking_pool_whitelist_account_id` field is stored immutably in the lockup contract's state and is exactly the value consulted by `select_staking_pool` when the (legitimate) owner later attempts to delegate/stake locked funds [7](#0-6) . This is precisely the trust mechanism the whitelist system was designed to protect, as documented: "the staking pool should guarantee that the delegated tokens can not be lost or locked... only approved (whitelisted) accounts of staking pool contracts can receive delegated tokens from lockup contracts" [8](#0-7) . If the owner is later funded on this squatted account (e.g., NEAR Foundation transfers the real grant directly to the pre-existing, correctly-owned account without realizing it was pre-deployed by a third party) and calls `select_staking_pool` for a pool the attacker controls, the attacker's malicious whitelist contract can simply return `true`, letting the owner stake into an attacker-controlled staking pool that never permits unstake/withdraw.

This mirrors the external Paraspace report's root cause class: an unprivileged, front-running attacker exploits a resource keyed deterministically to a victim's identity (Uniswap NFT balance slot vs. NEAR lockup account name) to pre-empt and corrupt a state that the victim/protocol will later rely on, at low attacker cost.

### Impact Explanation
This falls under "Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release... flows" and potentially "Unauthorized transfer, withdrawal, spending, or release of locked... NEAR through public-call... accounting failure reachable by an unprivileged user," since the legitimate, canonical lockup account for a given beneficiary can be permanently squatted with attacker-chosen `staking_pool_whitelist_account_id`, which is the sole gate protecting staked/delegated NEAR from being routed to a malicious, non-compliant staking pool controlled by the attacker.

### Likelihood Explanation
The attacker needs no privileges — only knowledge of (or the ability to guess/observe) the target `owner_account_id` and 3.5 NEAR to cover `MIN_ATTACHED_BALANCE`, which is cheap relative to the value of a large vesting/lockup grant. Because `owner_account_id`s for NEAR Foundation-sponsored vesting grants are often known or announced ahead of the actual `create()` transaction landing, front-running is realistic. The attack requires only a single successful `create()` call before the legitimate one.

### Recommendation
- Restrict `create()` so it can only be called by the `owner_account_id` itself or by a small set of pre-approved/privileged creators (e.g. require `predecessor_account_id == owner_account_id` or an allow-listed foundation caller), removing the ability for arbitrary third parties to pre-create a lockup account for someone else.
- Alternatively/additionally, incorporate a value only known to/controlled by the legitimate creator (e.g., a foundation-provided nonce/signature) into the derived account name, so the deterministic name cannot be pre-claimed by unrelated third parties.
- Emit and require explicit re-validation (e.g. an owner-confirmed whitelist parameter) before any funds beyond the minimal storage deposit are transferred into a lockup account, rather than assuming any correctly-owned lockup account was created by a trusted party.

### Proof of Concept
1. NEAR Foundation intends to grant a vesting lockup to `alice.near` and will later call `lockup-factory.create(owner_account_id="alice.near", ..., whitelist_account_id=<official-whitelist>)`.
2. Attacker observes this intent (e.g., public announcement, mempool) and front-runs by calling `lockup-factory.create(owner_account_id="alice.near", lockup_duration=0, vesting_schedule=None, release_duration=None, whitelist_account_id=<attacker-controlled-whitelist>)` with `attached_deposit = MIN_ATTACHED_BALANCE`, per `create()`'s public, unprivileged signature [9](#0-8) .
3. The deterministic account `sha256("alice.near")[..20].lockup-factory.near` is created with `owner_account_id = alice.near` but `staking_pool_whitelist_account_id` pointing to the attacker's malicious whitelist contract.
4. The Foundation's subsequent `create()` call for `alice.near` fails (account already exists) and its deposit is refunded via `on_lockup_create`'s failure branch [10](#0-9) ; the Foundation instead transfers the real grant balance directly to the existing (correctly-owned) lockup account, unaware of the tampered whitelist.
5. `alice.near`, believing the lockup is legitimate (it does list her as owner), later calls `select_staking_pool` for a pool controlled by the attacker; the attacker's malicious whitelist returns `true` [11](#0-10) , and Alice stakes/delegates locked NEAR into a staking pool that never allows unstaking/withdrawal.

### Citations

**File:** lockup/src/owner.rs (L12-41)
```rust
    pub fn select_staking_pool(&mut self, staking_pool_account_id: AccountId) -> Promise {
        self.assert_owner();
        assert!(
            env::is_valid_account_id(staking_pool_account_id.as_bytes()),
            "The staking pool account ID is invalid"
        );
        self.assert_staking_pool_is_not_selected();
        self.assert_no_termination();

        env::log(
            format!(
                "Selecting staking pool @{}. Going to check whitelist first.",
                staking_pool_account_id
            )
            .as_bytes(),
        );

        ext_whitelist::is_whitelisted(
            staking_pool_account_id.clone(),
            &self.staking_pool_whitelist_account_id,
            NO_DEPOSIT,
            gas::whitelist::IS_WHITELISTED,
        )
        .then(ext_self_owner::on_whitelist_is_whitelisted(
            staking_pool_account_id,
            &env::current_account_id(),
            NO_DEPOSIT,
            gas::owner_callbacks::ON_WHITELIST_IS_WHITELISTED,
        ))
    }
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

**File:** whitelist/README.md (L6-9)
```markdown
In order for the lockup contracts to be able delegate to a staking pool, the staking pool should faithfully implement the spec.
The staking pool should guarantee that the delegated tokens can not be lost or locked, such as the lockup contract should be
able to recover delegated tokens back to the lockup from a staking pool. In order to enforce this, only approved (whitelisted)
accounts of staking pool contracts can receive delegated tokens from lockup contracts.
```
