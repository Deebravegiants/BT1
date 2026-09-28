### Title
Pool `repay` refunds "excess" computed from the declared amount rather than measured receipt, paying refunds out of real custody to a caller who transferred nothing - (File: contracts/pool/src/ops/repay.rs)

### Summary
`ops::repay::apply` in `contracts/pool` resolves the credited repayment against the current debt ceiling and treats the remainder of the *declared* inbound amount as an overpayment refund. The refund path debits neither `cash` nor passes `require_reserves`, so a declared-but-never-transferred amount produces a real token payout from pool custody. This mirrors CVE-2017-8310's bug class: a length/amount field is trusted past the end of the data actually supplied — here, an amount parameter is trusted past the tokens actually received.

### Finding Description
A pool-level `repay` computes `net_repay` as `min(declared, current_debt_ceil)` and refunds `declared - net_repay` back to the payer. The refund is derived from the declared argument, not from a balance-delta measurement of what the caller actually pushed in. On a market with zero outstanding debt, `current_debt_ceil == 0`, the full-close branch makes `net_repay == 0`, the `RepayRoundsToZeroShares` assert passes on its `net_repay == 0` disjunct, and the *entire declared amount* is refunded out of real custody while the cash book is untouched. The repository's own test demonstrates custody draining with nothing transferred in: [1](#0-0) 

The same refund gap is documented for `ops::recapitalize::apply`, where the excess over the shortfall is likewise refunded from a declared inbound figure: [2](#0-1) 

### Impact Explanation
Theft of user funds. An unprivileged caller invokes `repay` (or `recapitalize`) on a market with zero (or small) debt, declaring an arbitrarily large amount up to the pool's custody balance, and receives a "refund" of funds that were never paid. Repeated or sized-to-custody calls drain supplier deposits directly. No debt position, oracle state, or privileged role is required.

### Likelihood Explanation
Reachable by any unprivileged address calling the pool's `repay` entrypoint against a market whose `current_debt_ceil` is zero — e.g., a newly listed market before any borrows, or any market fully repaid. The declared amount is bounded only by pool custody. The in-repo test `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` already reproduces custody draining end-to-end.

### Recommendation
Measure the inbound transfer by balance delta (`balance_after - balance_before` snapshot taken before any pull) and compute the excess refund only over the *received* amount, never the declared parameter. Additionally, reconcile the refund path with the cash book: any payout that is not backed by a measured inbound delta must revert. Apply the same fix to `ops::recapitalize::apply`'s excess-over-shortfall refund.

### Proof of Concept
1. Pick a market with zero total debt (`current_debt_ceil == 0`).
2. As an arbitrary address, call `pool::repay(payer, [(hub_asset, pool_custody_balance)])` with no prior token transfer to the pool.
3. `resolve_repay` takes the full-close branch, `net_repay = 0`, the full declared amount is treated as excess, and the refund transfers real custody tokens to `payer`. Confirmed by `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` at `contracts/pool/tests/flows.rs:3590`, which asserts `credited == 0` while custody is drained to `payer`.

### Citations

**File:** contracts/pool/tests/flows.rs (L3578-3610)
```rust
/// The refund gap is not specific to `recapitalize`. Two pool legs refund an
/// excess derived from a declared inbound amount, not from the cash book:
/// `ops::recapitalize::apply` (the excess over the shortfall) and
/// `ops::repay::apply` (the excess over the debt). Neither refund debits `cash`
/// or passes `require_reserves`.
///
/// A repay against a market with no debt makes the entire declared amount an
/// overpayment: `current_debt_ceil` is zero, so `resolve_repay` takes the
/// full-close branch and `net_repay` is zero. The `RepayRoundsToZeroShares`
/// assert in `ops::repay::accounting` passes on its `net_repay == 0` disjunct,
/// and the whole amount is refunded out of real custody with the book untouched.
#[test]
fn test_unfunded_repay_overpayment_refund_also_pays_out_of_custody() {
    let t = TestSetup::new();
    let token = token::Client::new(&t.env, &t.asset);
    let payer = Address::generate(&t.env);

    let custody_before = token.balance(&t.pool);
    let before = t.state_snapshot();
    assert_eq!(
        before.cash, custody_before,
        "fixture guard: book and custody must start in sync"
    );
    assert_eq!(before.borrowed, 0, "fixture must carry no debt");

    // Nothing transferred in, no debt to retire: the whole amount is "excess".
    let credited = t
        .client()
        .repay(&payer, &t.ract(0, custody_before))
        .get_unchecked(0)
        .actual_amount;
    assert_eq!(credited, 0, "no debt was retired, so nothing is credited");
    assert_unfunded_refund_drained_custody(&t, &payer, custody_before, &before);
```
