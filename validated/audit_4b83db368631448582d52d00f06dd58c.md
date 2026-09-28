### Title
Stale delegate grant reactivates when the account NFT returns to a former owner - ([File: contracts/controller/src/account.rs])

### Summary
The Sunshine bug class is "authorization material persisted before/without the state change that should invalidate it, so an unintended client ends up authorized." The analog in XOXNO Lending is the delegate-grant lifecycle: a delegate grant is keyed by the *granting owner's address* with no transfer epoch or invalidation on NFT transfer. When an account NFT moves to a new owner, the old owner's grants become dormant but are not deleted; if the NFT later returns to the original owner, the previously granted delegate silently regains full spending authority over the account — including `borrow`/`withdraw` to arbitrary recipients — without any fresh consent from the owner at that moment.

### Finding Description
`require_owner_or_delegate` admits a caller when it is an active position manager whose address appears in `get_delegates(env, account_id, owner)`, where `owner` is the account's *current* owner [1](#0-0) . The grant list is stored per `(account_id, owner)` and is never cleared on transfer; the docs state this plainly: "A grant records the owner's address, without a transfer epoch. It is inactive under another owner but can reactivate if the NFT returns" [2](#0-1) . This is pinned by tests: the grant dies on transfer but the same manager becomes live again under a fresh or returning owner context [3](#0-2) , and delegates "can choose external payout recipients, giving them broad economic control" [4](#0-3) .

Like the Sunshine cert persisted before PIN validation completed, the authorization artifact (the grant) survives a transition (NFT transfer away and back) that the owner reasonably believes invalidated it.

### Impact Explanation
Theft of user funds. A reactivated delegate can call `withdraw(caller=M, account_id, withdrawals, to=Some(M))` and `borrow(..., to=Some(M))` on the reacquired account, draining collateral and drawing debt up to the LTV limits (`require_owner_or_delegate` then `require_external_recipient` are the only gates; the recipient may be any external address) [5](#0-4) . The debt obligation also travels with the account to the owner.

### Likelihood Explanation
Medium. The attacker must already hold a delegate grant from the victim (i.e., be a governance-activated position manager the owner once opted into) and must wait for the NFT to return to that owner — for example the owner sells the account NFT and later buys an equivalent account back, or the NFT is routed through a marketplace/escrow and returned. The attacker cannot force the return, but once it happens the dormant grant re-arms automatically; `is_owner_or_delegate` performs only `caller == owner` or the stored-grant check, with no re-consent [6](#0-5) . Note this behavior is documented in INV-AUTH-02 and pinned by `new_owner_grant_overwrites_stale_grant`, so it is arguably a known design caveat rather than an undocumented defect; it is reported because the reactivation path grants authority without the current-owner's-fresh-grant semantics a user would expect.

### Recommendation
Bind each grant to an ownership epoch (e.g., store a transfer counter or the grant's ledger/`token_id` ownership generation alongside the owner in the `Delegates` entry) and have `is_owner_or_delegate` reject grants stamped under a previous ownership generation. Alternatively, purge the owner's delegate list in the position-NFT transfer hook (or on the controller side when ownership changes are next observed), matching the "transfer disables that owner's grants" expectation end-users have, rather than letting grants reactivate silently.

### Proof of Concept
1. Alice owns `account_id` A with collateral; governance has activated manager contract `M` via `set_position_manager(M, true)`.
2. Alice calls `add_delegate(alice, A, M)` — the grant is stored under `(A, alice)`.
3. Alice transfers NFT A to Bob (`position-nft transfer`). Under `owner = bob` the grant check `get_delegates(A, bob).contains(M)` fails, so `M` is correctly rejected (as `transfer_revokes_old_owners_delegates` shows).
4. Bob transfers NFT A back to Alice (repurchase, refund, escrow unwind). The stored `(A, alice)` grant is untouched, so `is_owner_or_delegate(A, M, alice)` returns true again.
5. `M` calls `withdraw(M, A, [collateral legs], Some(M))` — `require_owner_or_delegate` passes and funds leave to `M`; or `borrow(M, A, borrows, Some(M))` loading Alice's account with debt paid out to `M`.

No failure of the enclosing transaction rolls back the grant: the write was committed by `add_delegate` long before the transfer cycle that should have permanently invalidated it — the same "persisted before invalidation" shape as CVE-2024-45407.

### Citations

**File:** contracts/controller/src/account.rs (L115-139)
```rust
pub(crate) fn is_owner_or_delegate(
    env: &Env,
    account_id: u64,
    caller: &Address,
    owner: &Address,
) -> bool {
    if caller == owner {
        return true;
    }
    let active_manager =
        storage::get_position_manager(env, caller).is_some_and(|config| config.is_active);
    active_manager && storage::get_delegates(env, account_id, owner).contains(caller)
}

/// Requires the owner or a registered, active manager delegated by that owner.
pub(crate) fn require_owner_or_delegate(
    env: &Env,
    account_id: u64,
    caller: &Address,
    owner: &Address,
) {
    if is_owner_or_delegate(env, account_id, caller, owner) {
        return;
    }
    panic_with_error!(env, GenericError::NotAuthorized);
```

**File:** docs/reference/invariants.md (L31-34)
```markdown
Borrowing and withdrawal require the current NFT owner or an active position
manager delegated by that owner. Delegates can choose external payout recipients,
giving them broad economic control within the account's risk limits. Only the
owner can grant or revoke delegation.
```

**File:** docs/reference/invariants.md (L36-38)
```markdown
A grant records the owner's address, without a transfer epoch. It is inactive
under another owner but can reactivate if the NFT returns, unless an intervening
owner overwrites or purges the grant.
```

**File:** tests/test-harness/tests/controller/position_nft.rs (L81-113)
```rust
#[test]
fn transfer_revokes_old_owners_delegates() {
    let mut t = LendingTest::new().with_market(usdc_preset()).build();
    t.supply(ALICE, "USDC", 1_000.0);
    let account_id = t.account_id(ALICE);
    t.enable_delegate(ALICE, "MANAGER", account_id);

    t.nft_transfer(ALICE, BOB, account_id);

    // The manager's grant was stamped by ALICE; with BOB as owner it is dead.
    let result = t.try_borrow_as_to("MANAGER", account_id, "USDC", 10.0, "MANAGER");
    assert_contract_error(result, errors::NOT_AUTHORIZED);
}

#[test]
fn new_owner_grant_overwrites_stale_grant() {
    let mut t = LendingTest::new().with_market(usdc_preset()).build();
    t.supply(ALICE, "USDC", 1_000.0);
    let account_id = t.account_id(ALICE);
    let attrs = t.get_account_attributes(ALICE);
    t.enable_delegate(ALICE, "MANAGER", account_id);
    t.nft_transfer(ALICE, BOB, account_id);
    t.adopt_account(BOB, account_id, attrs.spoke_id, attrs.mode);

    // BOB re-grants; the stale ALICE grant is overwritten wholesale.
    t.enable_delegate(BOB, "MANAGER", account_id);
    t.borrow_as_to("MANAGER", account_id, "USDC", 10.0, BOB); // must succeed now

    assert!(
        t.borrow_balance_for(BOB, account_id, "USDC") > 9.0,
        "manager's borrow-as-to-BOB under the fresh grant must have landed"
    );
}
```

**File:** contracts/controller/src/positions/supply.rs (L147-157)
```rust
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_payments(env, withdrawals, payments::ZeroLeg::MeansAll);

    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
```
