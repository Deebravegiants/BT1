### Title
A borrower can permanently block liquidation and bad-debt cleanup by holding a dust collateral leg whose price feed reverts - (File: contracts/controller/src/positions/liquidation/plan.rs)

### Summary
The liquidation plan values **every** supply position of the target account inside `build_liquidation_plan`, and any panic in a single leg's price lookup aborts the entire transaction. Since an unprivileged borrower can supply a dust amount of any listed asset (including Aquarius LP tokens whose fair-value pricing can be pushed below its `min_pool_value_wad` floor by ordinary liquidity withdrawals), the borrower can make their own account unliquidatable on demand. The same leg also blocks standalone bad-debt cleanup, so the debt can only grow — an availability/insolvency analog of the MySQL optimizer crash/hang class.

### Finding Description
`build_liquidation_plan` in `contracts/controller/src/positions/liquidation/plan.rs` calls `risk::calculate_account_risk_totals` and `calculate_seizure_proportions`, which iterate all of the account's `supply_positions`. In `get_account_bonus_params` (`contracts/controller/src/positions/liquidation/math.rs:579-598`) and `calculate_seized_collateral` (`math.rs:383-385`), each leg calls `cache.cached_price(&hub_asset.asset)`. `cached_price` fails closed: a stale, out-of-band, or otherwise unavailable quote reverts the whole call. There is no mechanism to skip or drop an unpriceable leg — pro-rata seizure requires valuing all collateral.

The project's own threat model documents the consequence in DoS.1 (`docs/explanation/threat-model.md:364`): "Supply needs no price, so an indebted borrower can add a dust leg of any listed collateral and choose which feed outage shields the account. For an Aquarius LP leg, liquidity providers can cause that outage by withdrawing pool value below `min_pool_value_wad`. The same leg blocks bad-debt cleanup and force-socialization."

Reachable path, all unprivileged:

1. Attacker `supply` of a dust amount of an Aquarius LP-token collateral market into their account (supply requires no price check).
2. Attacker `borrow` a liquid asset against other collateral.
3. Attacker withdraws their own liquidity from the underlying Aquarius pool (an "own trade on Aquarius", in scope) so the LP fair-value quote drops below `min_pool_value_wad` and the price read panics.
4. Any `liquidate(liquidator, account_id, payments, seize_mode)` call reverts inside `build_liquidation_plan` before any repayment is processed — both `SeizeMode::Transfer` and `SeizeMode::Credit` hit the same `cached_price` calls, so neither mode bypasses it.
5. `check_bad_debt_after_liquidation`/standalone cleanup also iterates the same positions, so the insolvency cannot be force-socialized.

Unlike a normal fail-closed price outage, here the *attacker chooses which feed to break* and holds the switch via a dust leg that costs almost nothing.

### Impact Explanation
Permanent freezing of the liquidation channel for that account and permanent blocking of its bad-debt cleanup → protocol insolvency as interest accrues on unseizable debt. Because the shield is attacker-controlled and cheap (one dust deposit plus an LP withdrawal that can be reversed afterward), an underwater borrower can keep their account unliquidatable indefinitely, paying only dust collateral and gas.

### Likelihood Explanation
Medium. Requires the attacker to hold or acquire LP tokens in an Aquarius pool thin enough that their own withdrawal pushes fair value under `min_pool_value_wad`, and a listed LP-collateral market pricing that pool. Both are attacker-controlled actions; no privileged role, leaked key, or oracle dishonesty is needed — the LP pricing contract correctly reports "value below floor". Severity Medium, matching the source CVE class (availability-only, but here translating to insolvency risk rather than a mere crash).

### Recommendation
Make liquidation tolerant of a single unpriceable collateral leg — e.g., treat legs whose price read fails as zero-valued for the seizure plan and exclude them from `seized_collaterals` (a `SeizeEntry` for an unpriceable leg cannot be paid out anyway), or allow `clean_bad_debt`/`recapitalize` to proceed by writing down the debt against a partial seizure. Alternatively, enforce a minimum USD value on supply positions that can coexist with debt, so a dust leg cannot carry outsized veto power. Note the constraint: skipping the leg under-pays the liquidator unless the repayment plan is re-derived against the reduced collateral set.

### Proof of Concept
```text
// Attacker = borrower = LP holder
supply(attacker, other_collateral, large)        // normal collateral
supply(attacker, AQUA_LP_USDC_XLM, 1 unit)       // dust shield leg (supply needs no price)
borrow(attacker, USDC, near_max)
aquarius_pool.withdraw(attacker, liquidity)      // push LP fair value < min_pool_value_wad
// price for the LP token now panics in cached_price

// Any liquidator call:
liquidate(liq, attacker_id, [(USDC_hub_asset, X)], SeizeMode::Transfer)
// -> build_liquidation_plan -> calculate_account_risk_totals / get_account_bonus_params
// -> cached_price(AQUA_LP) reverts -> whole liquidation reverts

// Cleanup is equally blocked:
clean_bad_debt(attacker_id) // iterates same supply_positions -> same revert
```

I could not fully verify the price-aggregator `min_pool_value_wad` revert path or whether `clean_bad_debt` has a price-independent fallback (the `markets.rs` matches were not read in detail) — the finding stands on the documented DoS.1 mechanism and the verified fact that every collateral leg's `cached_price` is evaluated unconditionally in `plan.rs`/`math.rs` before any repayment is applied.