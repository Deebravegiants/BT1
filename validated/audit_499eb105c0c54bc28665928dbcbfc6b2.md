## Finding

### Title
Unprivileged lockup account squatting via unauthenticated `owner_account_id` and arbitrary `whitelist_account_id` in `LockupFactory::create` - (File: `lockup-factory/src/lib.rs`)

### Summary
`LockupFactory::create()` derives the lockup contract's account ID solely from a caller-supplied `owner_account_id` and lets the caller freely override the `staking_pool_whitelist_account_id` that the resulting lockup contract will trust for its entire lifetime, without verifying that the caller is actually the intended owner. Because the resulting account ID is deterministic and depends only on `owner_account_id`, any unprivileged account can pre-create ("squat") the lockup contract for a victim's `owner_account_id` before the legitimate deposit/creation transaction occurs, permanently blocking the real creation and/or planting an attacker-controlled whitelist contract that the lockup will trust for delegation decisions.

### Finding Description
`create()` computes the lockup account deterministically: [1](#0-0) 

```
pub fn create(
    &mut self,
    owner_account_id: ValidAccountId,
    ...
    whitelist_account_id: Option<ValidAccountId>,
) -> Promise {
    assert!(env::attached_deposit() >= MIN_ATTACHED_BALANCE, "Not enough attached deposit");
    let byte_slice = env::sha256(owner_account_id.as_ref().as_bytes());
    let lockup_account_id = format!("{}.{}", hex::encode(&byte_slice[..20]), env::current_account_id());
```

There is no check that `env::predecessor_account_id() == owner_account_id`, so *any* unprivileged account can pay `MIN_ATTACHED_BALANCE` and create a lockup contract for an arbitrary `owner_account_id` chosen by the attacker. Because the target account is derived only from a hash of `owner_account_id`, the resulting address is fully predictable ahead of time, e.g. before the real employer/foundation issues its official creation transaction for that same `owner_account_id`.

Compounding this, `whitelist_account_id` is fully attacker-controllable and, if supplied, unconditionally overrides the factory's canonical whitelist: [2](#0-1) 

```
// Defaults to the whitelist account ID given on init call.
let staking_pool_whitelist_account_id = if let Some(account_id) = whitelist_account_id {
    account_id.into()
} else {
    self.whitelist_account_id.clone()
};
```

This value is passed straight into the deployed `LockupContract::new`, which stores it immutably and trusts it completely for all future `select_staking_pool` decisions: [3](#0-2) [4](#0-3) 

The lockup README documents the entire security model of staking delegation as depending on this whitelist being the legitimate one approved by the NEAR Foundation: [5](#0-4) 

The test suite even demonstrates that a caller can freely supply a custom whitelist account at creation time with no additional authorization: [6](#0-5) 

### Impact Explanation
1. **Denial of service / permanent creation blocking**: Since the lockup account ID is deterministic on `owner_account_id` alone, an attacker can front-run and "squat" the account for any victim `owner_account_id` (e.g., a known future employee/vesting recipient) with the minimum attached deposit. When the legitimate creator (foundation/employer) later calls `create()` with the same `owner_account_id`, `create_account()` on an already-existing account fails, causing `on_lockup_create` to detect failure and simply refund the deposit — the legitimate lockup for that owner can never be created at that deterministic address again. This matches the "permanent freezing/unrecoverable lock" and "account-binding failure in ... pool-creation ... flows that break rightful redemption guarantees" impact categories.
2. **Delegation-safety bypass**: The squatted contract is initialized with an attacker-chosen `staking_pool_whitelist_account_id` (and can also omit `vesting_schedule`/`foundation_account_id`, or set arbitrary `lockup_duration`/`lockup_timestamp`). If any real funds are later sent to or interacted with through this address — including by the real `owner_account_id` (whose keys legitimately control `owner`-only methods since `owner_account_id` was attacker-supplied to match the victim) — any staking-pool selected via `select_staking_pool` will be checked against the attacker's malicious whitelist contract instead of the Foundation's, defeating the entire "staking pool has to be approved to prevent tokens from being lost, locked, or stolen" guarantee documented for this contract, allowing tokens delegated to a malicious pool to become unrecoverable.

### Likelihood Explanation
Exploitation only requires knowledge of a target `owner_account_id` (typically public/known in advance for vesting/lockup recipients) and `MIN_ATTACHED_BALANCE` (3.5 NEAR) — no privileged role is required, and the entry point (`create`) is a fully public, unauthenticated function call. The squatting race only requires the attacker to submit their transaction before the legitimate one for the same `owner_account_id`.

### Recommendation
- Require `env::predecessor_account_id() == owner_account_id` (or otherwise cryptographically bind account creation to the intended owner) before creating a lockup account on their behalf.
- Do not allow arbitrary callers to override `staking_pool_whitelist_account_id`; if customization is required, restrict it to a caller with an established trust relationship (e.g., the Foundation account) and/or require it to match a strict allow-list of approved whitelist contracts.
- Consider adding an explicit check in `on_lockup_create`/`create` to detect and reject squatting attempts, or use a nonce/attacker-unpredictable component in the derived account ID combined with owner authentication.

### Proof of Concept
1. Attacker learns that `alice.near` will eventually receive a lockup contract from `lockup-factory.near`.
2. Attacker calls `lockup-factory.near::create({owner_account_id: "alice.near", lockup_duration: 0, whitelist_account_id: "attacker-whitelist.near"})` with `attached_deposit = MIN_ATTACHED_BALANCE`, per [7](#0-6)  — no signature/relationship to `alice.near` is required.
3. This deterministically creates and deploys the lockup contract at `sha256("alice.near")[..20].lockup-factory.near`, per [8](#0-7) , with `owner_account_id = alice.near` and `staking_pool_whitelist_account_id = attacker-whitelist.near`.
4. When the Foundation later attempts the legitimate `create()` call for `alice.near`, the `create_account()` action fails because the account already exists, and `on_lockup_create` refunds the deposit and reports failure per [9](#0-8)  — the real lockup for `alice.near` can never be created at this address.
5. If Alice or the Foundation is unaware and interacts with the squatted contract, any staking pool selection will be validated only against `attacker-whitelist.near`, which the attacker fully controls (e.g., always returning `is_whitelisted = true`), enabling delegation of funds to a malicious staking pool.

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

**File:** lockup-factory/src/lib.rs (L390-425)
```rust
    #[test]
    fn test_create_lockup_with_custom_whitelist_success() {
        let mut context = VMContextBuilder::new()
            .current_account_id(account_factory())
            .predecessor_account_id(account_near())
            .finish();
        testing_env!(context.clone());

        let mut contract = LockupFactory::new(whitelist_account_id(), foundation_account_id());

        const LOCKUP_DURATION: u64 = 63036000000000000; /* 24 months */
        let lockup_duration: WrappedTimestamp = LOCKUP_DURATION.into();

        context.is_view = false;
        context.predecessor_account_id = String::from(account_tokens_owner());
        context.attached_deposit = ntoy(35);
        testing_env!(context.clone());
        contract.create(
            account_tokens_owner(),
            lockup_duration,
            None,
            None,
            None,
            Some(custom_whitelist_account_id()),
        );

        context.predecessor_account_id = account_factory();
        context.attached_deposit = ntoy(0);
        testing_env_with_promise_results(context.clone(), PromiseResult::Successful(vec![]));
        println!("{}", lockup_account());
        contract.on_lockup_create(
            lockup_account(),
            ntoy(30).into(),
            String::from(account_tokens_owner()),
        );
    }
```

**File:** lockup/src/lib.rs (L180-198)
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

**File:** lockup/README.md (L80-83)
```markdown
The owner can choose the staking pool for delegating tokens.
The staking pool contract and the account have to be approved by the whitelisting contract to prevent tokens from being lost, locked, or stolen.
Whitelisting contract is set at the moment of initializing the Lockup contract by [`staking_pool_whitelist_account_id`](https://github.com/near/core-contracts/blob/master/lockup/src/lib.rs#L190) field.
Once the staking pool holds tokens, the owner of the staking pool can use them to vote on the network governance issues, such as enabling transfers.
```
