### Title
Missing owner authorization lets any caller force-socialize an insolvent account's debt - (File: contracts/controller/src/positions/liquidation/mod.rs)

### Summary
`process_force_socialize_bad_debt` invokes the `BadDebtGate::InsolventOnly` cleanup path — which the code documents as "Owner-only" — but performs no owner/delegate check and not even `require_auth`. Any unprivileged address can therefore force bad-debt socialization on any insolvent account, bypassing the intended permission gate.

### Finding Description
The bad-debt gates are defined with explicit intent:

- `BadDebtGate::DustCapped` — "Permissionless: insolvent *and* collateral at or below the dust threshold."
- `BadDebtGate::InsolventOnly` — "Owner-only: insolvent alone, with no cap on the collateral left behind." [1](#0-0) 

The permissionless path is correctly authenticated and dust-gated in `process_clean_bad_debt` (`caller.require_auth()` + `clean_bad_debt_standalone` → `DustCapped`). However, the owner-only path `process_force_socialize_bad_debt` checks only `require_not_flash_loaning` and then calls `socialize_bad_debt(env, account_id, BadDebtGate::InsolventOnly)` on an attacker-supplied `account_id` — no `require_auth`, no `require_owner_or_delegate`, no ownership comparison against the account's NFT owner [2](#0-1) . `socialize_bad_debt` admits the call whenever `totals.total_debt > totals.total_collateral` with no dust cap [3](#0-2) .

This mirrors the reported bug class (improper permission validation over account-modifying operations): an operation designed to be restricted to the account owner is reachable by anyone.

### Impact Explanation
`socialize_bad_debt` calls `bad_debt::execute_bad_debt_cleanup`, which performs the supply-index write-down and cleanup of the victim account. An unprivileged attacker can force this on any account the moment it becomes insolvent, regardless of how much collateral remains. Consequences:

- The account owner's remaining collateral is consumed by the cleanup path immediately, skipping the normal liquidation flow where seizure is sized by measured repayments and the HF-based bonus curve — collateral that liquidators would have had to pay debt tokens to claim is disposed of without any repayment.
- Suppliers absorb the loss via the supply-index write-down at a time of the attacker's choosing (e.g., before market recovery could restore solvency, or front-running an orderly liquidation that would have left less bad debt).
- The attack is repeatable across all insolvent accounts and costs the attacker nothing.

Depending on how `execute_bad_debt_cleanup` disposes of residual collateral (not fully inspected), this is theft/permanent loss of the owner's residual collateral and premature socialized loss to suppliers — qualifying as theft of user funds / protocol insolvency acceleration. Severity: High if residual collateral is burned/forfeited without repayment; at minimum Medium given the explicit owner-only invariant is violated.

### Likelihood Explanation
Any authenticated-or-even-unauthenticated caller can invoke the entrypoint with a target `account_id`. The only precondition is `total_debt > total_collateral`, which occurs naturally during price drawdowns and is precisely when owners would want to control the timing of socialization (e.g., to deleverage, repay, or wait out a price wick). No capital, timing, or privileged position is required, so likelihood is high once any account crosses insolvency.

### Recommendation
In `process_force_socialize_bad_debt`, authenticate and authorize the caller against the target account before socializing:

```rust
pub(crate) fn process_force_socialize_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    validation::require_authorized_caller(env, caller);
    let account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    socialize_bad_debt(env, account_id, BadDebtGate::InsolventOnly);
}
```

This restores the documented "Owner-only" semantics while leaving `process_clean_bad_debt` permissionless for dust-capped cases.

### Proof of Concept
1. Victim account `V` holds collateral and debt; an oracle update pushes `V` to `total_debt > total_collateral` while still holding significant collateral (above the dust cap, so `clean_bad_debt` would revert with `CannotCleanBadDebt`).
2. Attacker `A` (unrelated to `V`, no delegation) calls the controller's force-socialize entrypoint with `account_id = V`.
3. `process_force_socialize_bad_debt` passes `require_not_flash_loaning`, then `socialize_bad_debt(V, InsolventOnly)` admits the call and runs `execute_bad_debt_cleanup`: `V`'s debt is written down via the supply index and the account is cleaned up — without `A` ever proving ownership or repaying anything.
4. `V`'s residual collateral is disposed of via the cleanup path rather than an incentive-priced liquidation, and suppliers absorb the write-down at `A`'s chosen moment.

### Citations

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-249)
```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
}

/// Admission condition for bad-debt socialization.
#[derive(Clone, Copy, PartialEq)]
enum BadDebtGate {
    /// Permissionless: insolvent *and* collateral at or below the dust threshold.
    DustCapped,
    /// Owner-only: insolvent alone, with no cap on the collateral left behind.
    InsolventOnly,
}

/// Requires open debt and the selected insolvency gate, then cleans up the account.
fn socialize_bad_debt(env: &Env, account_id: u64, gate: BadDebtGate) {
    let mut cache = Context::new(env);
    let account = storage::get_account(env, account_id);

    assert_with_error!(
        env,
        !account.borrow_positions.is_empty(),
        CollateralError::DebtPositionNotFound
    );

    let totals = risk::calculate_account_risk_totals(
        env,
        &mut cache,
        &account.supply_positions,
        &account.borrow_positions,
    );

    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);

    bad_debt::execute_bad_debt_cleanup(env, &mut cache, account_id, &account, &totals);
}

/// Socializes insolvent debt when remaining collateral is at or below the dust cap.
pub(crate) fn clean_bad_debt_standalone(env: &Env, account_id: u64) {
    socialize_bad_debt(env, account_id, BadDebtGate::DustCapped);
}

/// Socializes debt exceeding collateral without a dust cap, outside flash loans.
pub(crate) fn process_force_socialize_bad_debt(env: &Env, account_id: u64) {
    validation::require_not_flash_loaning(env);
    socialize_bad_debt(env, account_id, BadDebtGate::InsolventOnly);
}
```
