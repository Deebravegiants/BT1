### Title
Self-inflicted Aquarius LP price outage via dust collateral leg bricks liquidation and `clean_bad_debt` for an underwater account — (`contracts/price-aggregator/src/providers/aquarius.rs`)

### Summary
A borrower can make their own account permanently unliquidatable — and simultaneously block `clean_bad_debt` — by holding a dust supply position in an Aquarius LP-token collateral and then draining that Aquarius pool below its configured `min_pool_value_wad` floor using their own liquidity. Because `supply` performs no price check, the poison leg can be planted at any time, even while the LP price is already failing. Once the pool is under the floor, every strict price read for that asset returns `OracleError::InsufficientAquariusLiquidity`, the controller's risk-total computation panics, and every valuation-dependent path against the victim reverts. The attacker can restore liquidity at will to unfreeze the account, so this is a repeatable, on-demand DoS of the liquidation and bad-debt-cleanup machinery that lets debt accrue into protocol insolvency.

### Finding Description
`providers::aquarius::read` recomputes the pool's total value on every read and rejects it when `pool_value_wad < lp.min_pool_value_wad` with `InsufficientAquariusLiquidity` (`contracts/price-aggregator/src/providers/aquarius.rs:118-122`). Pool value is `price_wad * total_shares / share_unit`, so removing reserves (an ordinary LP withdrawal, an unprivileged action) lowers `price_wad` and pushes the pool under the floor.

On the controller side, `build_liquidation_plan` unconditionally calls `risk::calculate_account_risk_totals` over **all** of the victim's supply and borrow positions (`contracts/controller/src/positions/liquidation/plan.rs:34-44`), and `calculate_ltv_collateral_wad`/`sum_debt_usd` call `cache.cached_price(&hub_asset.asset)` for every leg (`contracts/controller/src/risk/totals.rs:84-93`, `:48-59`). Strict reads fail closed per INV-ORACLE-01, so a single unpriceable leg aborts the entire liquidation — repayment cannot be targeted at "healthy" legs only. `clean_bad_debt` shares the same valuation path, so the dust leg also blocks bad-debt write-down.

Crucially, `supply` needs no price (the threat model notes "Supply needs no price"), so the attacker can plant the dust LP leg *after* the outage begins — they do not even need foresight. The project's own audit test `tests/test-harness/tests/controller/audit_supply_stale_shield.rs:4-58` demonstrates the identical mechanics with a stale Reflector leg: plant dust collateral → `liquidate` reverts `PRICE_FEED_STALE`, `clean_bad_debt` reverts, `withdraw` reverts — and the same account is instantly liquidatable again once the leg prices. With an Aquarius LP asset, the attacker induces the same condition with their own pool withdrawal instead of waiting for feed staleness.

### Impact Explanation
- **Protocol insolvency:** the attacker's underwater account cannot be liquidated and its bad debt cannot be written down while the shield holds; interest keeps accruing, converting a marginal account into realized protocol bad debt.
- **Temporary freezing of funds:** all suppliers of the borrowed asset are exposed to the frozen debt; the victim's own collateral is also frozen (`withdraw` reverts), but that is a self-inflicted cost the attacker accepts to protect a net-negative position.
- The attack is per-transaction cheap: one dust `supply` plus one Aquarius withdrawal. It can be toggled on/off at will by adding/removing pool liquidity, so it can be sustained exactly during the window where the position is underwater.

### Likelihood Explanation
Fully reachable by a single unprivileged address: `controller::supply` (no price check on deposit), an ordinary `withdraw` on the attacker's own Aquarius pool liquidity (allowed: "own trades on Aquarius"), and no privileged state. It requires the protocol to list an Aquarius LP share token as collateral and the attacker to control enough of that pool's liquidity to push `price_wad * total_shares / share_unit` under `min_pool_value_wad` — feasible for thin pools, pools admitted near their floor (the ops alert `LendingLpPoolValueNearFloor` in `services/lending-exporter/ops/alerts.yml:42-48` explicitly warns that crossing 1.0x makes "accounts holding this leg … unliquidatable"), or pools the attacker bootstraps. No oracle dishonesty is needed — the provider itself reports the failure.

### Recommendation
- Valuation should skip or floor-to-zero a supply leg whose strict price fails when computing *liquidation* totals (treat unpriceable collateral as zero collateral rather than aborting), so a poisoned dust leg reduces HF instead of shielding it. `clean_bad_debt` must get the same treatment or it stays bricked.
- Alternatively/additionally: refuse `supply` (or make it price-check the deposited asset) when the account has outstanding debt, so a failing-feed leg cannot be planted on an indebted account; and enforce a minimum first-supply amount per collateral market so dust legs cannot be attached for ~1 stroop.
- Size `min_pool_value_wad` with enough headroom that a single LP cannot cross the floor with one withdrawal, and monitor pools approaching it before listing-dependent accounts accumulate.

### Proof of Concept
Conceptual trace mirroring `audit_supply_stale_shield.rs` with an attacker-controlled outage:

1. Governance lists Aquarius LP token `LP` as collateral in the attacker's spoke with floor `min_pool_value_wad = F`.
2. Attacker supplies `C` units of USDC to account `A`, supplies a dust amount (e.g. `0.001`) of `LP`, then `borrow`s ETH against total collateral.
3. Attacker calls Aquarius `withdraw_liquidity` on the pool backing `LP` until `price_wad * total_shares / share_unit < F`. From then on `providers::aquarius::read` returns `Err(InsufficientAquariusLiquidity)` (`aquarius.rs:120-122`).
4. USDC price drops; account `A` is deeply underwater. Any liquidator calling `Controller::liquidate(caller, A_id, [ETH leg], SeizeMode::Transfer)` reverts inside `build_liquidation_plan → calculate_account_risk_totals → cached_price(LP)` (`plan.rs:34`, `totals.rs:85`).
5. `Controller::clean_bad_debt` on `A_id` reverts on the same price read.
6. Attacker keeps the pool drained for as long as the position is net-negative, letting interest convert the debt into protocol bad debt; when convenient, they re-add liquidity — the pool exceeds `F` again and the account is liquidatable once more, showing the outage is fully attacker-toggled.

If the dust leg was not planted beforehand, step 2's `LP` supply can be executed after step 3 — `supply` performs no valuation, confirmed by the passing `try_supply` under a stale feed in `audit_supply_stale_shield.rs:26-30`.