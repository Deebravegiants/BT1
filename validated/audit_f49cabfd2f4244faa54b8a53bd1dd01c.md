### Title
Liquidator extracts a liquidation bonus on same-token collateral legs that could be netted 1:1 — (File: contracts/controller/src/positions/liquidation/plan.rs)

### Summary

The bug class from the report — paying an intermediary a discount/bonus for a "swap" where `base == quote` and no exchange service is needed — maps directly onto XOXNO Lending's liquidation seizure. `build_liquidation_plan` seizes collateral **pro-rata across every supply leg**, including legs whose asset is the *same token* the liquidator repays. Repaying `X` units of token T against an account that also supplies token T seizes `X * (1 + bonus)` units of T, although the identical economic result — cancelling supply against debt in the same market — is available at 1:1 through `net_settle_collateral_against_debt` / `pool_net_settle_call` in `contracts/controller/src/strategies/legs.rs`. The bonus on the same-token leg is a gratuitous haircut charged to the borrower, exactly like the `scaledOfferFactor` discount paid to a flash swapper for exchanging ether for ether.

### Finding Description

`plan::build_liquidation_plan` (contracts/controller/src/positions/liquidation/plan.rs) computes `calculate_seizure_proportions` and then `calculate_seized_collateral(env, account, totals.total_collateral, &repayment, cache)` over **all** supply positions. There is no same-asset exclusion or net-settlement branch: a debt leg in `HubAssetKey{hub, T}` is repaid while a supply leg in `HubAssetKey{hub', T}` (or even the same hub) is seized at `repay_usd * one_plus_b`. The math pipeline (`seizure_usd_i`, `base_ray`, `bonus_ray` per docs/reference/formulas.md `total_seizure_usd = repay_usd × one_plus_b`) applies the HF-based bonus to the same-token leg identically to any other leg.

Contrast with the strategy path: `process_repay_debt_with_collateral` explicitly branches on `collateral == debt` and routes to `net_settle_collateral_against_debt`, which moves zero tokens and settles at 1:1 — the codebase itself acknowledges that same-market positions must be netted without an exchange premium (contracts/controller/src/strategies/repay_debt_with_collateral.rs:57-67, legs.rs:163-229). The liquidation path has no such netting: `spoke_liquidation_combo.rs::test_spoke_liquidation_with_split_collateral` proves the pro-rata seizure hits the USDT supply leg while the liquidator repays USDT debt in the same transaction.

### Impact Explanation

The borrower loses `repay_amount × bonus_bps` of the same token on every liquidation touching a same-token collateral leg — value that a 1:1 netting would not have consumed. Worse, the pool experiences a real cash drain: the liquidator pushes `X` of token T to the pool and `SeizeMode::Transfer` pays out `X(1+b)` of T from pool cash, so the pool is a net payer of `X·b` tokens for a pure debt/collateral cancellation that needed no market service. Over repeated liquidations this is direct, quantifiable theft of collateral value from liquidated users (the bonus is split between liquidator and the `liquidation_fees` protocol bucket), with no corresponding risk absorbed — the "exchange" is T→T.

### Likelihood Explanation

Reachable by any unprivileged liquidator via `liquidate(caller, account_id, debt_payments, SeizeMode::Transfer)` whenever a liquidatable account (HF < 1) holds both a borrow position and a supply position denominated in the same token across any hubs — a common configuration since hub/spoke markets and `PositionMode::Multiply` flash positions routinely book same-token debt-and-collateral pairs (the harness test `declaring_the_debt_asset_alongside_real_collateral_is_a_plain_leveraged_open` shows an account holding ETH supply and ETH debt as a supported state). No timing, oracle manipulation, or privilege is needed beyond an already-unhealthy account.

### Recommendation

In `build_liquidation_plan` / `calculate_seized_collateral`, exclude same-asset legs from the pro-rata seizure up to the amount that can be netted 1:1, and settle them via the existing `pool_net_settle_call` before computing the bonus-bearing seizure for the remaining cross-asset value. If a debt payment leg matches a collateral leg's asset, the seized amount for that leg must be capped at `paid_amount` (no `one_plus_b` factor), so the liquidator receives no bonus for a T→T "swap".

### Proof of Concept

Setup mirrors `test_spoke_liquidation_with_split_collateral` (tests/test-harness/tests/controller/spoke_liquidation_combo.rs:63-108):

1. Alice (any user) supplies 5,000 USDC and 4,000 USDT, borrows 8,000 USDT — a permitted state (same-token supply+debt is supported, per `flash_position_mode_and_asset_edges.rs`).
2. USDC price drops to $0.60 → HF < 1.
3. Liquidator calls `liquidate(LIQUIDATOR, alice_id, [(hub, USDT, 500 USDT)], SeizeMode::Transfer)`.
4. `calculate_seized_collateral` seizes pro-rata: the USDT leg loses `~500 × (1+b) × (4,000/7,000)` USD of USDT — i.e. the liquidator receives **more USDT back from the pool than the USDT they paid in**, pocketing `~X·b` USDT while cancelling USDT debt that netting would have cleared 1:1.

The same-asset portion of the seizure is pure bonus extraction, identical in shape to `scaledOfferFactor` being applied when `cBase == cQuote`: a discount paid for a conversion that is no conversion at all.