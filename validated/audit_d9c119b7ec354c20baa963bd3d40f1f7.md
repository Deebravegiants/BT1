### Title
Unprivileged front-running of deterministic lockup accounts with an attacker-supplied whitelist address permanently blocks legitimate lockup creation - (File: lockup-factory/src/lib.rs)

### Summary
`LockupFactory::create()` derives the new lockup's account ID deterministically from only the `owner_account_id` (`sha256(owner_account_id)` prefix), and lets the caller override the trusted, immutable `staking_pool_whitelist_account_id` set at factory `new()` with an arbitrary attacker-chosen `whitelist_account_id` parameter. Any unprivileged account can pre-create the deterministic lockup account for any target `owner_account_id` before the legitimate creator (e.g. the NEAR Foundation) does, permanently occupying that address and embedding a malicious "whitelist" contract that the true beneficiary can never replace.

### Finding Description
The lockup account name is computed purely from `owner_account_id`, with no dependence on the caller's identity: [1](#0-0) 

`create()` is a public, payable method with no check that `env::predecessor_account_id()` equals or is authorized for `owner_account_id`, and it accepts an optional `whitelist_account_id` that overrides the factory's trusted, immutable `self.whitelist_account_id`: [2](#0-1) 

Because NEAR account creation is unique, once an account ID is created it can never be created again. An unprivileged attacker can call `create(owner_account_id = <victim>, ..., whitelist_account_id = Some(<attacker-controlled account>))` with the minimum attached deposit before the legitimate party (e.g., NEAR Foundation) issues the real grant creation for that same `owner_account_id`. This permanently squats the deterministic address with a lockup contract whose `staking_pool_whitelist_account_id` field is attacker-controlled and immutable (no setter exists in `lockup/src/owner.rs` to change it after `new()`), since the whitelist address is only ever set once during `new()` and it's the sole authority validated in `select_staking_pool` via `ext_whitelist::is_whitelisted`: [3](#0-2) 

This is the direct analog of the external report's root cause: an address that should be a hardcoded/immutable trust anchor (the bridge address in the EVM report; here, the staking-pool whitelist account) is instead accepted as an attacker-influenced parameter on a public entrypoint, allowing substitution of the trusted authority.

### Impact Explanation
Since the lockup account name is a pure function of `owner_account_id`, once an attacker squats it with a malicious whitelist, the legitimate lockup creation transaction for that beneficiary will always fail at `create_account()` (the account already exists), and the factory's failure path only refunds the *legitimate caller's* deposit — it can never re-target a different account ID for that beneficiary. The intended beneficiary is permanently denied a properly configured lockup, and if funds are later sent into the squatted account (e.g., mistakenly by the foundation, or because the beneficiary still uses it believing it's the real grant contract), the victim's `select_staking_pool` calls are validated only against the attacker's fake whitelist rather than the NEAR Foundation's real one, letting a bogus "staking pool" be treated as approved. This matches the "Permanent freezing / unrecoverable lock ... in lockup release ... factory refund ... flows" and "Authorization / state-machine bypass ... beyond intended authority" impact categories.

### Likelihood Explanation
The attack requires only a public `create()` call with the minimum attached deposit (`MIN_ATTACHED_BALANCE`, 3.5 NEAR) and knowledge of the target `owner_account_id` a grantee is expected to use — no privileged role, signer, or key compromise is needed. The main cost is the attacker's deposit and gas, which is small relative to the potential value of a blocked token grant, making this economically viable griefing for high-value targets known in advance (e.g., publicly announced NEAR Foundation grant recipients).

### Recommendation
Do not allow the `create()` caller to supply an alternate whitelist account; always use the factory's immutable `staking_pool_whitelist_account_id` set at `new()` (drop the `Option<ValidAccountId>` parameter or restrict it to a call made/authorized by the foundation account). Additionally, incorporate the caller's identity or a factory-controlled nonce/salt into the derived lockup account name (or require that only the foundation/authorized caller can create a lockup for a given `owner_account_id`) so that an unprivileged actor cannot pre-empt/squat the deterministic account address for an arbitrary beneficiary.

### Proof of Concept
1. Attacker deploys/owns a malicious contract `evil-whitelist.near` that always returns `true` for `is_whitelisted`.
2. Attacker calls `lockup_factory.create(owner_account_id = "victim.near", lockup_duration, None, None, None, whitelist_account_id = Some("evil-whitelist.near"))` with `MIN_ATTACHED_BALANCE` attached, per [2](#0-1) .
3. This creates the deterministic account `sha256("victim.near")[..20].<factory>` and initializes it with `staking_pool_whitelist_account_id = "evil-whitelist.near"`.
4. When the NEAR Foundation later attempts to create the legitimate lockup for `"victim.near"` via the same factory, `create_account()` on the same deterministic address fails because the account already exists, and only the (legitimate) caller's deposit is refunded via `on_lockup_create` — the victim's grant lockup can never be (re)created at the correct address, per [4](#0-3) .

### Citations

**File:** lockup-factory/src/lib.rs (L107-133)
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
