### Title
Pool `repay`/`recapitalize` refund pays unfunded "overpayment" out of real custody, draining supplier funds - (File: contracts/pool/src/ops/repay.rs)

### Summary
The BEE driver's bug class is an ownership/settlement-contract violation: the error path released a buffer it did not own, and the caller released it again — one resource freed twice. The analog in XOXNO Lending is the same shape at the settlement layer: `ops::repay::apply` and `ops::recapitalize::apply` treat the *declared* inbound amount as received cash and then "refund" the unused portion back out of the pool's real token balance, without checking that the funds ever arrived and without debiting accounting cash or checking reserves. One unit of pool custody is thus consumed twice — once by the book entry that never debits it, and once by the refund `transfer_out` — letting an unprivileged payer drain the pool by declaring repayments/recapitalizations it never funded.

### Finding Description
Both legs follow the same pattern:

1. `repay::accounting` resolves `action.amount` against the position's debt shares, computes `overpayment = amount - net_repay`, credits only `net_repay` to cash, and commits the book [1](#0-0) .
2. `repay::apply` then calls `outcome.cache.transfer_out(payer, outcome.overpayment)` [2](#0-1) . `transfer_out` performs a real `token.transfer` from the pool's own address and explicitly does *not* adjust accounting cash or call `require_reserves` [3](#0-2) .
3. `recapitalize::apply` is identical: `applied = amount.min(backing_shortfall)`, `refund = amount - applied`, then `transfer_out(&payer, refund)` [4](#0-3) .

Neither function measures the pool's actual balance delta (there is no `balance_before`/`balance_after` anywhere in these ops — contrast `payments.rs::refund_controller_balance_delta` in the controller, which refunds only the *measured* delta). The refund is derived purely from the declared `amount`. The in-repo test `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` documents the consequence: a `repay` with a declared amount equal to the pool's whole custody, against a market with zero debt, credits nothing to the book yet pays the full "overpayment" out of custody [5](#0-4) .

The vulnerable reachable shape for an unprivileged address:

- **Direct `pool.repay` on a market with no open debt for that position.** `resolve_repay` takes the full-close branch, `net_repay = 0`, `burned = 0` (allowed by the `net_repay == 0` disjunct of the `RepayRoundsToZeroShares` assert), and the entire declared `amount` becomes `overpayment`, refunded from custody. The attacker supplies nothing — or under-delivers with a fee-on-transfer/rebasing debt token — and receives real tokens.
- **`controller.recapitalize`** is explicitly permissionless (`recapitalize` is in-scope), and the pool-side refund has the same unfunded-refund gap: any declared `amount` above `backing_shortfall` (which is 0 on a healthy market) is refunded from custody.

### Impact Explanation
Theft of user funds. Each call pays out tokens from the pool's real token balance while the accounting `cash`/`borrowed` books are untouched, so the protocol's books still claim full backing while custody is drained. Repeating the call (or declaring `amount = custody`) extracts the entire physical balance of a market; suppliers then cannot withdraw because the tokens are gone — i.e., permanent loss absorbed by LPs. For the under-delivery variant (fee-on-transfer asset), the attacker does deposit, but the refund is computed on the declared amount rather than the measured receipt, so the difference is still stolen each iteration.

### Likelihood Explanation
The repay path requires only an ordinary `repay` call with a declared `amount` exceeding the position's debt — no privileged role, no oracle manipulation, no special market state. A market/position with zero debt makes *any* declared amount a pure overpayment. The recapitalize variant is similarly permissionless and needs only `amount > backing_shortfall`, which holds trivially on any healthy market. The only uncertainty is whether the pool's `repay` entrypoint additionally gates callers to the controller; the production test invokes `client().repay` directly with a freshly generated, unfunded payer, indicating the leg itself performs no inbound-funding verification.

### Recommendation
Measure receipts rather than trusting the declared amount, matching the controller's own `balance_delta_since` pattern:

- Record `balance_before` of the pool's token balance at entry, and cap `overpayment`/`refund` at `min(declared_excess, measured_delta)`; alternatively require the caller to pre-fund and compute the refund from the actual custody increase.
- Route refunds through `debit_cash` (or at minimum `require_reserves`) so the refund cannot exceed what the books say the pool holds.
- Same fix in `ops::recapitalize::apply`.

### Proof of Concept
The repo already contains it: `contracts/pool/tests/flows.rs::test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` — a payer with no transfer-in calls `repay` with `amount == pool custody` on a zero-debt market; `actual_amount` credited is `0` and the entire amount is refunded out of custody, leaving the book claiming full reserves while the balance is gone. Analogously, `recapitalize(payer, hub_asset, amount)` with `amount > backing_shortfall` refunds `amount - shortfall` from custody. [6](#0-5)

### Citations

**File:** contracts/pool/src/ops/repay.rs (L25-33)
```rust
pub(crate) fn apply(
    env: &Env,
    payer: &Address,
    action: &PoolAction,
) -> (PoolPositionMutation, MarketStateSnapshot) {
    let outcome = accounting(env, action);

    outcome.cache.transfer_out(payer, outcome.overpayment);
    (outcome.mutation, outcome.snapshot)
```

**File:** contracts/pool/src/ops/repay.rs (L44-60)
```rust
    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    assert_with_error!(
        env,
        net_repay == 0 || burned.raw() > 0,
        GenericError::RepayRoundsToZeroShares
    );

    let position = position.checked_sub(env, burned);
    cache.burn_debt(burned);

    cache.credit_cash(net_repay);

    let snapshot = cache.commit();
    let mutation = cache.position_mutation(position, net_repay);
```

**File:** contracts/pool/src/cache/cash.rs (L46-53)
```rust
    pub(crate) fn transfer_out(&self, recipient: &Address, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        if amount == 0 {
            return;
        }
        let tok = token::Client::new(&self.env, &self.params.asset_id);
        tok.transfer(&self.env.current_contract_address(), recipient, &amount);
    }
```

**File:** contracts/pool/src/ops/recapitalize.rs (L44-66)
```rust
pub(crate) fn accounting(
    env: &Env,
    hub_asset: HubAssetKey,
    amount: i128,
) -> RecapitalizationOutcome {
    require_nonneg_amount(env, amount);
    let mut cache = ops::renewed_market(env, &hub_asset);

    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();

    RecapitalizationOutcome {
        cache,
        mutation: PoolAmountMutation {
            actual_amount: applied,
        },
        refund,
    }
```

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
