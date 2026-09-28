### Title
Dust Aquarius-LP collateral leg plus attacker-drained pool liquidity bricks liquidation and bad-debt cleanup of an underwater account - (File: contracts/price-aggregator/src/providers/aquarius.rs)

### Summary
The price aggregator rejects an Aquarius LP share price with `InsufficientAquariusLiquidity` whenever the pool's total value falls below the configured `min_pool_value_wad`. Liquidation and `clean_bad_debt` must strictly price *every* supply and debt leg of the account, so a borrower who plants a dust supply leg of an Aquarius LP token can make their account unliquidatable and unsocializable by withdrawing their own liquidity from that Aquarius pool — a crash/DoS analog to CVE-2020-14837 where a crafted input reliably hangs the target operation.

### Finding Description
- `providers::aquarius::read` computes `pool_value_wad` from the pool's live reserves and total shares and returns `Err(OracleError::InsufficientAquariusLiquidity)` when `pool_value_wad < lp.min_pool_value_wad` (`contracts/price-aggregator/src/providers/aquarius.rs:118-122`). The pool value is driven entirely by on-chain Aquarius reserves, which any liquidity provider can shrink by removing liquidity.
- `supply` needs no price read, so a borrower can open a dust supply leg in an LP-token market even while that asset is unpriceable — confirmed by `audit_supply_stale_shield` and `audit_liquidate_and_clean_stale_leg`, where `try_supply` succeeds with an unusable feed (`tests/test-harness/tests/controller/audit_supply_stale_shield.rs:26-35`).
- Risk totals and liquidation planning call `cache.cached_price(&hub_asset.asset)` for every supply/debt leg via `Context::load_markets`/`cached_price` (`contracts/controller/src/risk/totals.rs:84-97`). The strict price read propagates the oracle error and aborts the whole transaction, so one poisoned leg reverts `liquidate` and `clean_bad_debt` (both revert with the oracle error in the same tests, lines 51-58 and 36-40 respectively).
- Unlike a stale third-party feed, the `min_pool_value_wad` floor is under the attacker's control: if the attacker is a liquidity provider in a shallow Aquarius pool that backs a listed LP collateral, they withdraw reserves until `pool_value_wad < min_pool_value_wad` and keep them withdrawn. The threat model itself names this vector in DoS.1 (`docs/explanation/threat-model.md:364`).

### Impact Explanation
While the outage lasts, no liquidator can repay any debt leg of the account (`liquidate` reverts), permissionless `clean_bad_debt` reverts, and the governed force-socialization path that computes account totals is also blocked. Interest accrues on debt that cannot be liquidated or written down, growing protocol insolvency; collateral and debt are frozen in place — a temporary freezing of funds and a step toward pool insolvency (the account's real collateral ratio keeps deteriorating while every resolution path is bricked). The attacker can sustain the freeze indefinitely by staying below the floor, or even alternate withdrawal/redeposit to time the shield.

### Likelihood Explanation
Requires a listed Aquarius-LP collateral market and an Aquarius pool shallow enough that one LP (the attacker, possibly the dominant LP) can push `pool_value_wad` below `min_pool_value_wad` at acceptable cost. The attacker's own loss is limited to foregone LP yield; the dust collateral leg costs a few stroops. All entrypoints used — `supply`, plus own trades on Aquarius — are unprivileged.

### Recommendation
Make collateral pricing resilient to a single bad leg: value a supply leg whose price read fails as zero (or skip it from seizure) rather than aborting, at least on the liquidation and `clean_bad_debt` paths; alternatively, reject `supply`/`top-up` of an asset whose strict price is currently unavailable, and/or enforce a `min_pool_value_wad` high enough that draining a listed pool is uneconomic relative to plausible bad debt.

### Proof of Concept
1. Attacker (borrower) supplies real collateral, borrows to the LTV limit.
2. Attacker calls `supply` with a dust amount of an Aquarius LP token whose pool is shallow (accepted: supply does not require a price).
3. Attacker withdraws their own liquidity from that Aquarius pool until `pool_value_wad < min_pool_value_wad` (`aquarius.rs:120-121`).
4. Collateral price drops / debt accrues → account goes below HF 1.
5. Any `liquidate(account_id, ...)` reverts with `InsufficientAquariusLiquidity` because `calculate_account_risk_totals`/`cached_price` strictly prices the LP leg; `clean_bad_debt(account_id)` reverts the same way. Debt and collateral remain frozen until the attacker restores liquidity.

Mechanism demonstrated by existing tests: `audit_liquidate_and_clean_bricked_by_unpriceable_dust_leg` (`tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs:36-40`) shows `liquidate` and `clean_bad_debt` both reverting on an unpriceable planted leg, recovering once the price resolves.