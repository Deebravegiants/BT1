## Analog Vulnerability Found

### Title
Front-runnable, unauthorized `create()` call in `LockupFactory` lets any unprivileged caller permanently squat a target owner's deterministic lockup account - (File: `lockup-factory/src/lib.rs`)

### Summary
The reported UniswapV2Factory bug stems from a deterministically-derived address (the wrapper address, computed via CREATE2 from the collection address) being usable as a key to prematurely register state (`delegates` mapping) before the legitimate deployment happens, permanently blocking correct future use. The same root-cause pattern — an attacker-callable, fully public function that derives a target account/address deterministically from a caller-supplied identifier and immediately performs a one-shot, unrepeatable creation against it — exists in `LockupFactory::create`.

### Finding Description
`LockupFactory::create` computes the lockup account name purely as a deterministic function of the `owner_account_id` argument supplied by the caller and the factory's own account id, with no check that the caller is `owner_account_id`, the foundation, or any other authorized party: [1](#0-0) [2](#0-1) 

Specifically: [3](#0-2) 

`lockup_account_id` is `sha256(owner_account_id)[..20]` hex-encoded, concatenated with the factory's account id — fully predictable/precomputable by anyone who knows the target `owner_account_id` (e.g. a known NEAR Foundation employee/investor account slated to receive a lockup). Because NEAR account names are globally unique and the `create_account()` Promise action will simply fail if the name is already taken, whoever calls `create()` first for a given `owner_account_id` permanently claims that account name, deploying the lockup contract there with attacker-chosen `lockup_duration`, `lockup_timestamp`, `vesting_schedule` (or none), `release_duration`, and `whitelist_account_id`: [4](#0-3) 

There is no verification anywhere in `create()` that the caller is authorized to create a lockup on behalf of `owner_account_id`, nor any reservation/allow-list mechanism preventing a stranger from squatting the deterministic name for a fee of only `MIN_ATTACHED_BALANCE` (3.5 NEAR): [5](#0-4) 

### Impact Explanation
An unprivileged attacker can precompute the exact deterministic account id that the NEAR Foundation (or any funder) would later use to deploy a compliant lockup contract for a specific beneficiary, and front-run it with a cheap `create()` call using bogus parameters (e.g. no `vesting_schedule`, arbitrary `lockup_duration`, or malicious `staking_pool_whitelist_account_id`). Once that account name exists, the legitimate, correctly-configured lockup for that beneficiary can never be deployed at the expected deterministic address — this is a permanent, irrecoverable denial of service on the lockup creation flow for that specific owner, matching the "Permanent freezing / unrecoverable lock ... in lockup release ... factory refund ... flows" and "account-binding failure in ... pool-creation ... flows that breaks single-execution or rightful redemption guarantees" impact categories.

### Likelihood Explanation
The precondition is trivial: `owner_account_id` values destined for lockups (employees, investors, grant recipients) are frequently known or guessable ahead of time (e.g., published team/investor account names). `create()` is a fully public, unauthenticated, `#[payable]` method requiring only the minimum attached deposit, so any unprivileged account can execute the front-run with a single transaction the moment the target identity becomes known, well before the legitimate funder transacts.

### Recommendation
Require that the `owner_account_id` either signs/authorizes the `create()` call (e.g., via a pre-registered allow-list maintained by the foundation, or by requiring `predecessor_account_id() == owner_account_id` or a foundation-signed authorization), or bind creation rights to the foundation/authorized funder account rather than allowing arbitrary unprivileged callers to claim any target's deterministic lockup account name.

### Proof of Concept
1. Attacker observes/learns that `alice.near` is scheduled to receive a lockup from `lockup.near` factory (deterministic name `sha256("alice.near")[..20]_hex.lockup.near`).
2. Attacker calls `lockup.near.create({owner_account_id: "alice.near", lockup_duration: ..., vesting_schedule: None, ...})` attaching only `MIN_ATTACHED_BALANCE` (3.5 NEAR), from their own account.
3. `LockupFactory::create` computes the same deterministic `lockup_account_id` and successfully deploys a lockup contract there under attacker-chosen terms.
4. When the NEAR Foundation later attempts the legitimate `create()` call for `alice.near` with the real vesting terms, the `create_account()` Promise fails because the account already exists; `on_lockup_create` refunds the foundation's deposit but the correct lockup for `alice.near` can never be created at the expected address, permanently disrupting the intended vesting/lockup flow for that beneficiary.

### Citations

**File:** lockup-factory/src/lib.rs (L34-34)
```rust
const MIN_ATTACHED_BALANCE: Balance = 3_500_000_000_000_000_000_000_000;
```

**File:** lockup-factory/src/lib.rs (L107-116)
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
```

**File:** lockup-factory/src/lib.rs (L117-140)
```rust
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
```
