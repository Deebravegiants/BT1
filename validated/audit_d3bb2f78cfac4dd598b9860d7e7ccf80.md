### Title
Self-inflicted Aquarius LP feed outage shields an underwater account from liquidation and bad-debt cleanup - (File: contracts/price-aggregator/src/providers/aquarius.rs)

### Summary
A borrower can hold a dust-sized supply position in a collateral priced by an Aquarius LP source, then withdraw liquidity from that same Aquarius pool to push its value below `min_pool_value_wad`. The LP price read fails closed with `InsufficientAquariusLiquidity`, every required-valuation path on the account aborts, and the account becomes unliquidatable and un-cleanable for as long as the pool stays thin. Interest keeps accruing on the debt, converting a recoverable undercollateralized account into protocol bad debt.

### Finding Description
XOXNO Lending prices Aquarius LP share collateral by computing a fair LP price from the pool's reserves and total shares, then rejects the observation when the total pool value falls below a configured floor. In `contracts/price-aggregator/src/providers/aquarius.rs:118-122`, `read` computes `pool_value_wad` and returns `OracleError::InsufficientAquariusLiquidity` when it is below `lp.min_pool_value_wad`. Aquarius pools are permissionless: any address that holds LP shares can withdraw its liquidity at will, shrinking `total_shares` and the reserves proportionally.

The controller treats every required price strictly. `fetch_prices` in `contracts/controller/src/external/price_aggregator.rs:17-29` panics with `OracleNotConfigured` on any missing feed, and strict reads propagate provider errors such as `InsufficientAquariusLiquidity` / `PriceFeedStale`. `build_liquidation_plan` in `contracts/controller/src/positions/liquidation/plan.rs:34-44` calls `risk::calculate_account_risk_totals` over all of the account's supply and borrow positions, so one unpriceable collateral leg aborts the entire liquidation before the seizure plan is built. INV-ORACLE-01 documents that a missing or unusable required price aborts valuation-dependent operations including liquidation, and bad-debt cleanup performs the same risk computation, so `clean_bad_debt` fails the same way.

Crucially, planting the shield requires no price: `supply` does not need a valid price for the supplied asset (the threat model states "Supply needs no price"), so the borrower can add a dust leg of the LP collateral at any time, including while its feed is already degraded. The harness test `audit_supply_setup_blocks_liquidation_via_stale_dust_leg` in `tests/test-harness/tests/controller/audit_supply_stale_shield.rs:4-72` demonstrates the mechanism end to end with a stale feed: `liquidate` and `clean_bad_debt` both revert on the poisoned account while a twin account without the leg liquidates normally.

Because the attacker is both the borrower and an LP in the referenced pool, no privileged role, oracle misbehavior, or third-party dependency failure is needed — just one permissionless LP withdrawal plus a dust `supply` call.

### Impact Explanation
While the shield holds, the attacker's account cannot be liquidated (`liquidate` reverts during risk calculation) and cannot be socialized (`clean_bad_debt` reverts the same way). Interest continues to accrue on the unbacked debt. Suppliers in the debt market bear the eventual loss through supply-index write-downs when the debt is finally cleaned, i.e., protocol insolvency / theft of supplier funds rather than a mere availability hiccup. The same leg also blocks force-socialization, so governance recovery paths are impaired too.

### Likelihood Explanation
Medium. Requirements: a listed collateral whose price source is an Aquarius LP pool with liquidity shallow enough that a single withdrawal pushes it under `min_pool_value_wad`, and an attacker who supplies dust of that LP token to their own account. Both actions are permissionless and cheap; the attacker forfeits only the dust collateral and LP position. The window persists exactly as long as the attacker keeps the pool below the floor and can be re-established after any refill.

### Recommendation
- Price collateral legs independently where possible: skip supply positions that fail valuation only after all healthy collaterals are already exhausted in the pro-rata plan, or treat an unpriceable dust leg as zero-value with its seizure skipped rather than aborting the whole plan.
- Alternatively, weight the decision: omit unpriceable legs from `calculate_account_risk_totals` when their value is below a dust floor, so a dust shield cannot block liquidation of a materially collateralized account.
- Set `min_pool_value_wad` conservatively high at admission and monitor pool depth, since the floor is the only barrier between normal operation and an attacker-controlled outage.

### Proof of Concept
1. List collateral token `LP` whose oracle source is an Aquarius pool with configured `min_pool_value_wad`.
2. Attacker acquires a modest LP share of that pool, calls `controller::supply` to add a dust `LP` leg to their own borrowing account (succeeds — supply does not require a valid price).
3. Attacker borrows against other collateral near the LTV limit; market moves (or interest accrues) until HF < 1.
4. Attacker calls `withdraw` on the Aquarius pool, reducing `pool_value_wad` below `min_pool_value_wad`.
5. `aquarius::read` returns `InsufficientAquariusLiquidity` (`aquarius.rs:120-122`); the strict price fetch fails; `build_liquidation_plan` reverts inside `calculate_account_risk_totals` (`plan.rs:34-44`). Every `liquidate` and `clean_bad_debt` call on the account reverts.
6. Debt grows via interest while unliquidatable; when finally cleaned, `clean_bad_debt` writes the supply index down and suppliers absorb the loss.

This mirrors the existing harness demonstration in `tests/test-harness/tests/controller/audit_supply_stale_shield.rs:4-72` (stale-feed variant) and `tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs:4-54`, with the outage triggered by a permissionless LP withdrawal instead of feed staleness.