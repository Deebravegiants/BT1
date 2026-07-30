### Title
Permanent front-running/squatting of deterministic lockup account name in `LockupFactory::create` causes irrecoverable DoS of legitimate lockup creation - (File: `lockup-factory/src/lib.rs`)

### Summary
The `lockup-factory` contract's `create` method derives the new lockup contract's `AccountId` purely as a deterministic function of the caller-supplied `owner_account_id` (`sha256(owner_account_id)[..20]` as hex, concatenated with the factory account), with no binding to the caller's identity, no uniqueness guard, and no existence check before issuing the `create_account()` action. This mirrors the reported Solana `pump-science` bug (a required account is derivable from public seeds and can be created without the intended owner's permission), except here the "seed" is simply the intended lockup beneficiary's account id.

### Finding Description
In `LockupFactory::create`: [1](#0-0) 

the `lockup_account_id` is computed solely from `owner_account_id` — not from `env::predecessor_account_id()`, a nonce, or any value the intended owner controls. Any unprivileged account can call `create` for an arbitrary `owner_account_id` (e.g., a known team member, investor, or foundation beneficiary), attaching only the `MIN_ATTACHED_BALANCE`, with trivial/undesired parameters (e.g., `lockup_duration = 0`, no vesting schedule). Because NEAR only requires the immediate parent account (the factory itself, acting as predecessor in the receipt) to authorize the `CreateAccount` action — not the `owner_account_id` — this call succeeds and permanently occupies the deterministic account name `sha256(owner_account_id)[..20].<factory>`.

When the legitimate funder (e.g., the NEAR Foundation) later calls `create` for the same `owner_account_id` with the real vesting schedule, the identical `lockup_account_id` is computed, the `Promise::new(lockup_account_id).create_account()` action fails because the account already exists, and the whole batch fails. The `on_lockup_create` callback then only refunds the attached deposit — it does not, and cannot, retry under a different account id: [2](#0-1) 

Because the account name is a pure hash of `owner_account_id` with no salt/nonce, there is no way to ever create the intended lockup for that owner through this factory again — the account name is permanently squatted by attacker-controlled code (or, in the harmless case, permanently blocked with a `lockup_duration=0` contract).

### Impact Explanation
This matches the "Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release ... vesting termination ... factory refund" impact category. An unprivileged attacker can permanently deny a specific beneficiary (whose account id is public knowledge, e.g. a known investor/employee) from ever receiving a lockup contract through this factory, and/or force a malformed lockup (e.g. `lockup_duration = 0`, no vesting) to be squatted at that deterministic address before the legitimate high-value lockup transaction lands, since front-running is possible on a public mempool.

### Likelihood Explanation
Likelihood is realistic: `create_staking_pool`-style factories on NEAR are commonly invoked by known/whitelisted beneficiary account ids that are public prior to the real funding transaction (e.g., announced token allocations). Any account can call `create` with minimal `MIN_ATTACHED_BALANCE` before the legitimate transaction executes, requiring no special privilege — only an unprivileged function call.

### Recommendation
Bind the derived `lockup_account_id` to something the true owner/funder controls rather than a bare hash of the public `owner_account_id`, e.g., require a signature/attestation from `owner_account_id`, or use a factory-managed unique identifier (e.g., an on-chain nonce/registry as in `staking-pool-factory`'s `staking_pool_account_ids` set) combined with the owner. Additionally, restrict `create` to only be callable once per `owner_account_id` in a way that cannot be raced by an unrelated caller, and consider validating that `predecessor_account_id` is authorized (e.g., only the foundation or a designated funder) before allowing lockup creation for a given owner.

### Proof of Concept
1. Attacker observes (via public governance/allocation announcements) that `owner_account_id = "alice.near"` is scheduled to receive a lockup from `lockup-factory`.
2. Attacker computes `sha256("alice.near")[..20]` and calls `create(owner_account_id="alice.near", lockup_duration=0, ...)` on the factory with `MIN_ATTACHED_BALANCE`, from any unprivileged account. This succeeds and deploys a lockup contract at `<hash>.factory` with a zero/garbage duration and no vesting.
3. The foundation later calls `create(owner_account_id="alice.near", ...)` with the intended real vesting schedule and larger deposit.
4. The `Promise::new(lockup_account_id).create_account()` action fails because the account already exists; `on_lockup_create` runs the failure branch and refunds the deposit [3](#0-2) .
5. Alice's legitimate lockup can never be created through this factory for her account id — permanent DoS/loss of intended vesting arrangement.

### Citations

**File:** lockup-factory/src/lib.rs (L117-138)
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
