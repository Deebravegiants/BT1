### Title
Stranded supply shares surviving a bad-debt wipeout drain fresh deposits via the supply-index floor - (File: contracts/pool/src/interest.rs)

### Summary
`apply_bad_debt_to_supply_index` socializes unpaid debt by shrinking the supply index pro-rata, but clamps the result at `SUPPLY_INDEX_FLOOR_RAW` (RAY/1000) instead of zero. When a bad-debt seizure consumes the entire supplied value, surviving suppliers keep scaled shares that still unscale to a positive claim. The market is not tombstoned, so a fresh depositor can supply real cash into the wiped market, and the old "freed" shares withdraw it — a use-after-free of written-down supply claims.

### Finding Description
In `contracts/pool/src/ops/seize.rs:24-28`, a `Borrow`-side `PoolSeizeEntry` computes `bad_debt = unscale_borrow_ceil_ray(position)`, calls `interest::apply_bad_debt_to_supply_index`, then `cache.burn_debt(position)`. In `contracts/pool/src/interest.rs:73-89`, the reduction is `new_supply_index = supply_index * (value - capped)/value`, then `cache.set_supply_index(new_supply_index.max(SUPPLY_INDEX_FLOOR_RAW))`. When `bad_debt >= total_supplied_value`, `reduction_factor` is zero and the index lands exactly on the floor — not zero — so every holder of `supplied` scaled shares retains a claim of `scaled * floor` > 0.

The pool test `test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard` in `contracts/pool/tests/interest.rs:431-494` demonstrates the exact sequence on the raw `Cache`:

1. Alice holds scaled supply; a borrower's scaled debt is seized with `apply_bad_debt_to_supply_index` + `burn_debt`. Index clamps to `SUPPLY_INDEX_FLOOR_RAW`, cash = 0.
2. `cache.unscale_supply_floor(alice_scaled)` still returns > 0 — a stranded claim on a market with zero cash.
3. Bob deposits `alice_stranded` units of fresh cash (`mint_supply` + `credit_cash`). Books become insolvent: `total_owed > cash`.
4. Alice calls `resolve_withdrawal(i128::MAX, alice_scaled)` and withdraws exactly Bob's deposit. Bob's claim now exceeds remaining cash — the fresh depositor lost funds.

The reachable path mirrors this on the controller: `clean_bad_debt` (`contracts/controller/src/positions/liquidation/mod.rs:196-243`) or a liquidation that triggers `check_bad_debt_after_liquidation` (`apply.rs:301-315`) calls `pool_seize_positions_call`, which runs the same seize leg. Afterwards, any user can `supply` into that (hub, token) book — no code in the supply path checks `supply_index == SUPPLY_INDEX_FLOOR_RAW` or marks the market dead — and legacy suppliers can `withdraw` against their floored residual shares.

### Impact Explanation
Theft of user funds / protocol insolvency: written-down shares that should be economically dead retain a positive floor claim. Each fresh deposit into the wiped market is immediately claimable by pre-wipeout suppliers, up to their stranded residual, permanently draining new depositors.

### Likelihood Explanation
Requires a bad-debt event large enough to zero the reduction factor — i.e., a seizure where unpaid debt ≥ total supplied value of that market, or cumulative write-downs reaching the floor. This is exactly the scenario `clean_bad_debt`/`force_socialize` exist for. Once the index sits at the floor, exploitation needs only ordinary `supply` by a victim and `withdraw` by a legacy holder — no privileged call, no oracle manipulation beyond what already made the debt bad.

### Recommendation
When `apply_bad_debt_to_supply_index` clamps to `SUPPLY_INDEX_FLOOR_RAW`, tombstone the market: block new `supply`/`create_strategy` into a floored market (e.g., a `supply_index > floor` precondition or a wiped flag), or burn/zero the residual scaled supply so no stranded claim can later unscale to cash. Alternatively, gate withdrawals in floored markets on `cash >= total owed`.

### Proof of Concept
1. Bob supplies asset X; Alice borrows against X-collateral in the same market book.
2. Oracle price crashes; a liquidator repays Alice's debt down to the dust band, then anyone calls `clean_bad_debt(account_id)` — or the liquidation itself triggers `check_bad_debt_after_liquidation` — invoking `seize_positions` with the borrow leg. `apply_bad_debt_to_supply_index` caps `bad_debt` at total supplied value and clamps `supply_index` to `SUPPLY_INDEX_FLOOR_RAW`; `burn_debt` removes the debt. Bob's scaled supply survives as a floored residual claim on a now-empty market.
3. Carol supplies X into the same market (no guard on the floored index).
4. Bob calls `withdraw` for X; `resolve_withdrawal` unscales his floored scaled amount and `require_reserves` passes because Carol's cash is present. Bob receives Carol's deposit; Carol's scaled claim exceeds remaining cash — permanent loss.

Note: I could not exhaustively confirm that no production entrypoint blocks supply into a floored-index market; the in-repo unit test names the guard as the thing the raw cache lacks, and the searches I ran found no index-floor check in the controller's `require_can_supply` path or pool supply ops.