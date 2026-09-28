### Title
Sub-3-decimal sole-collateral positions can enter a "dead band" where every liquidation reverts, letting debt accrue unbacked - (File: contracts/controller/src/positions/liquidation/math.rs)

### Summary
`whole_unit_repayment` leaves the curve quote unchanged when the account's debt falls in the gap between `unit_at_bonus` (one collateral unit's worth of debt) and `unit_repayment` (one unit plus margin). In that window the quote backs less than one whole unit, so `calculate_seized_collateral` floors the partial seizure leg to zero, drops it, and `build_liquidation_plan`/`liquidate` reverts for *every* offered payment. Any unprivileged borrower can open a position with a single sub-3-decimal collateral and size the debt so that the position becomes stuck in this unliquidatable state once HF < 1.

### Finding Description
For a solvent account whose only supply position is an asset with `asset_decimals < MIN_BORROWABLE_ASSET_DECIMALS`, `normalize_repayment_plan` calls `whole_unit_repayment` to promote a sub-one-unit quote. The promotion has three branches in `math.rs`:

- Line 266-268: if the quote already backs `unit_with_margin`, keep it.
- Line 275-280: if `unit_at_bonus >= D + R` (whole-unit value at bonus covers debt plus one unit per debt leg), promote to full close.
- Line 287-289: if `unit_repayment >= D`, keep the original `quote_usd`.

When `unit_at_bonus < D + R` *and* `unit_repayment >= D`, the function returns the unmodified `quote_usd`, which by premise (`quote_usd * (1 + b) < unit_with_margin`) backs less than one whole unit of collateral. Then in `calculate_seized_collateral` (math.rs:401-416), a partial seizure leg for a sub-`MIN_BORROWABLE_ASSET_DECIMALS` asset floors to whole units, producing `seizure_ray = 0`; the leg is skipped at line 419-421. With the only supply leg dropped, `seized` is empty, `release_unbacked_repayment` strips the entire repayment (plan.rs:76-79), and the plan is rejected — `liquidate` reverts with `InvalidPayments` for any offered `debt_payments`. The docs confirm the behavior: "while `floor(U / (1 + b)) - R < D <= ceil((U + m) / (1 + b))`, neither rule 1 nor rule 2 applies ... every offer reverts until accrual or a price move ends that state" (docs/reference/formulas.md:305-308).

An attacker reaches this state entirely through unprivileged entrypoints: `supply` a sub-3-decimal asset as the sole collateral, `borrow` a different asset sized so that after a price move or interest accrual the risk debt lands strictly inside the band. There is no minimum-seizure escape hatch: the band's width is `R + margin` (one unit of each debt leg plus `U/1_000_000`), which for low-priced debt units can be arbitrarily small, but the attacker controls the borrow size and debt accrues deterministically through the band's lower edge.

### Impact Explanation
Temporary freezing of funds / protocol insolvency. While stuck, no liquidator can repay the debt in any amount — the position is unliquidatable despite HF < 1. If remaining collateral exceeds the $5 `BAD_DEBT_USD_THRESHOLD`, permissionless `clean_bad_debt` is also gated (`is_socializable_bad_debt`, curve.rs:25-27), so the debt keeps accruing interest against suppliers until accrual pushes `D` above `unit_repayment` or governance runs `force_socialize_bad_debt`. All interest accrued during the stuck window is unbacked and is written down onto the debt market's suppliers via `apply_bad_debt_to_supply_index`. The attacker retains the borrowed tokens; the cost is only the sub-3-decimal collateral, which can be dust-sized.

### Likelihood Explanation
Requires a listed market with `asset_decimals < 3` usable as collateral and a price/accrual path into the band — both attacker-influenced but not fully attacker-controlled (the band is narrow and depends on the stamped bonus `b` and debt-unit values `R`). The attacker can iterate: create many small positions so at least one lands in the band, since each attempt costs only gas plus the collateral. Severity is bounded — accrual eventually exits the band — matching a Medium.

### Recommendation
In `whole_unit_repayment`, when `unit_repayment >= snap.total_debt` but `unit_at_bonus < full_close_ceiling`, promote the quote to `snap.total_debt` (full close) instead of returning `quote_usd`. A full close sets `full_close`/`repays_all_debt`, the sub-3-decimal leg rounds up to the held unit(s) (math.rs:405-407), and liquidation succeeds rather than reverting on every offer. Alternatively, when the kept quote cannot back one whole unit, treat the position as a one-unit sale by clamping `ideal` to `unit_at_bonus` so at least one unit is seized.

### Proof of Concept
1. List/enable a collateral asset `LOW` with `asset_decimals = 2` (below `MIN_BORROWABLE_ASSET_DECIMALS`), price such that one whole unit is worth `U` (e.g., $10).
2. Attacker calls `supply` to deposit `k` whole units of `LOW` as the account's only supply position, then `borrow` of a 6-decimal stablecoin `D` such that after a small price drop or accrual the account satisfies `HF < 1` and `floor(U/(1+b)) - R < D <= ceil((U + max(U/1e6, 1))/(1+b))` where `R` is one stablecoin unit in WAD.
3. Any liquidator calls `liquidate(liquidator, account_id, [(debt_asset, amount)], SeizeMode::Transfer)` for any `amount`: `build_liquidation_plan` → `normalize_repayment_plan` → `whole_unit_repayment` returns the unchanged curve quote → `calculate_seized_collateral` floors the `LOW` leg to zero units → `seized` empty → revert (`InvalidPayments`). `clean_bad_debt` reverts with `CannotCleanBadDebt` while `C > $5` or `D <= C`. The debt accrues unbacked until `D` grows past `unit_repayment`, at which point liquidation succeeds but all interim interest is socialized onto `debt_asset` suppliers.