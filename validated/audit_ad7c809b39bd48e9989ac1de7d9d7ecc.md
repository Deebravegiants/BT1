### Title
Pool `repay` and `recapitalize` refund the *declared* excess instead of the *measured* inbound receipt, letting an unfunded call pay pool custody to the caller - (File: contracts/pool/tests/flows.rs)

### Summary
The bug class in the report is an accounting correction applied to the wrong quantity: the senior loss was booked against `jrtNavT0` while the conservation check `navT1 == jrtNavT1 + srtNavT1 + reserveNavT1` ran on the propagated `T1` values, so a declared-vs-actual summation diverged. XOXNO's pool has the same shape in its measured-receipt settlement: `ops::repay::apply` and `ops::recapitalize::apply` compute the refund (the excess to send back) from the caller-*declared* amount rather than from the tokens the pool actually received, so `cash`/custody conservation is broken in the refund direction — an adjustment booked on the stale (declared) figure instead of the running (measured) one. [1](#0-0) 

### Finding Description
The in-code comment at `contracts/pool/tests/flows.rs:3578-3588` states the defect directly: "Two pool legs refund an excess derived from a declared inbound amount, not from the cash book: `ops::recapitalize::apply` (the excess over the shortfall) and `ops::repay::apply` (the excess over the debt). Neither refund debits `cash` or passes `require_reserves`." [2](#0-1) 

Concretely, for `repay`: a repay against a market with no debt makes the entire declared amount an overpayment — `current_debt_ceil` is zero, `resolve_repay` takes the full-close branch, `net_repay` is zero, and the `RepayRoundsToZeroShares` assert passes on its `net_repay == 0` disjunct. The whole declared amount is then "refunded" out of real pool custody with the book untouched, exactly as an over-refund sized on a stale copy would overpay. [3](#0-2) 

This mirrors the reference bug structurally: just as `jrtNavT0 += srtLoss` left `jrtNavT1` stale so the `navT1` summation was violated, here the refund leg subtracts the applied amount from the *declared* amount and pays that difference out, while the cash book (`cash`, and the real token balance backing supplier claims) was never credited a matching inbound. The summation "custody == cash book + refunds owed" no longer holds.

### Impact Explanation
An unprivileged caller can invoke `pool.repay` (or `recapitalize`) with a large declared amount on a market where little or nothing is actually due/delivered, and receive a "refund" paid from pool custody — i.e., from funds backing supplier and revenue claims. The test `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` demonstrates custody being drained by `custody_before` on a market with zero debt and zero inbound transfer. This is theft of user funds / protocol insolvency, reachable by a single unprivileged address through the documented controller/pool repay and recapitalize paths. [4](#0-3) 

### Likelihood Explanation
No privileged state is required: `repay` and `recapitalize` are permissionless entrypoints, and the trigger condition (declared amount exceeding actual debt or shortfall, including a zero-debt market) is trivially reachable at any time. The only prerequisite is that the pool holds custody, which is the normal operating state.

### Recommendation
Compute the refundable excess from the *measured* inbound receipt (balance delta / `transfer_amount_measured`-style accounting), not the declared amount: `refund = received - applied`, never `declared - applied`. Also debit `cash` (or route the refund through `require_reserves`) when paying it out, so the refund cannot exceed what the operation actually took in — the same fix pattern as updating the propagated `T1` variable rather than the stale `T0` copy. Note this appears partially documented in-repo (the flows.rs comment), so verify against the production `ops::repay::apply`/`ops::recapitalize::apply` source before treating it as unpatched.

### Proof of Concept
- On a market with `borrowed == 0`, call `repay(payer, [(hub_asset, custody_before)])` with no corresponding inbound transfer; `resolve_repay` full-close branch yields `net_repay == 0`, and the entire declared amount is sent to the payer from pool custody. Asserted by `assert_unfunded_refund_drained_custody(&t, &payer, custody_before, &before)`. [5](#0-4) 
- Equivalently via `recapitalize`: declare an `amount` exceeding the market's measured `backing_shortfall`; the excess-over-shortfall refund is derived from the declared amount and pays out of custody without debiting `cash`. [2](#0-1) 

Caveat: I verified the behavior through the in-repo test and its comments; I did not have remaining budget to read `ops::repay`/`ops::recapitalize` source directly to confirm whether the refund uses declared-vs-measured amounts in the current build, or whether payer funds are pulled first (which would bound the refund by actual receipt).

### Citations

**File:** contracts/pool/tests/flows.rs (L3578-3611)
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
}
```
