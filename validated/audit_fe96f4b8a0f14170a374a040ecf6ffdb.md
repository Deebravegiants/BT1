### Title
Borrower permanently hides from liquidation-threshold downgrades via the `clears_min_hf` skip gate, staying non-liquidatable on stale risk stamps - (File: contracts/controller/src/risk/params.rs)

### Summary
CVE-2018-1121 is an enumeration-evasion race: a process manipulates ordering to avoid being seen by a scan. The analog in XOXNO Lending is a parameter-refresh scan that an account can evade. `update_account_threshold` is the only path that restamps a position's stored `liquidation_threshold`/`liquidation_bonus`/`liquidation_fees` to the current spoke config. Inside `apply_gated_liquidation_params`, when the new tuple favors the liquidator and the account's hypothetical health factor under the new threshold is below 1.05, the function silently returns without restamping. The account keeps its old, more generous stored threshold forever. Since `calculate_account_risk_totals` computes the health factor from the *stored* per-position threshold, an account whose true (current-config) HF is already below 1 can keep displaying a stale HF above 1 and is unreachable by `liquidate`, which requires `totals.health_factor < Wad::ONE` in `build_liquidation_plan`.

### Finding Description
Every `AccountPosition` carries a snapshot of the listing's risk tuple (`loan_to_value`, `liquidation_threshold`, `liquidation_bonus`, `liquidation_fees`), seeded at supply time in `Account::get_or_create_supply_position` (common/src/types/controller.rs:326-341). Risk gates never read the live config: `calculate_account_risk_totals_body` weights collateral by `position.liquidation_threshold` (contracts/controller/src/risk/totals.rs:193-198) and `liquidate` admits an account only when that stored-parameter HF is below 1 (contracts/controller/src/positions/liquidation/plan.rs:40-44).

`update_account_threshold(caller, has_risks, account_ids)` is permissionless (any authorized caller) and iterates accounts calling `sync_account_thresholds` → `refresh_supply_risk_params` with `RiskRefreshScope::FullTuple` (params.rs:124-144). The LTV restamp is unconditional, but the liquidation tuple goes through `apply_gated_liquidation_params` (params.rs:68-93):

```rust
if favors_liquidator(position, effective_config)
    && !account.debt_free()
    && !clears_min_hf(env, cache, account, hub_asset, position, effective_config.liquidation_threshold)
{
    return;   // silently keeps the OLD threshold
}
```

`clears_min_hf` recomputes HF with only this leg's threshold swapped to the new value and requires HF ≥ `THRESHOLD_UPDATE_MIN_HF_RAW` (1.05). So whenever a governance change lowers a listing's liquidation threshold (or raises bonus / lowers fees), every account whose *new* HF would be below 1.05 keeps its old stamps — and the skip is silent, so repeated calls can never force the update. This mirrors the CVE exactly: the scan (`update_account_threshold` iterating `account_ids`) is evaded by the scanned entity positioning itself so the scan passes over it.

Because liquidation eligibility is computed on the stored tuple, a gap between `LT_old` and `LT_new` creates a hiding band: for `0.9 → 0.5`, an account with `0.5·C/D < 1` (truly insolvent-grade) still shows `stale HF = 0.9·C/D ≥ 1` and reverts liquidations with `HealthFactorTooHigh`, while `clears_min_hf` on `LT_new` returns `< 1.05` so the restamp is skipped on every attempt. The account is permanently unliquidatable until debt grows past `LT_old·C`, accruing bad debt the entire time.

### Impact Explanation
Protocol insolvency / delayed-loss socialization. After a risk parameter tightening (the normal governance response to a deteriorating asset), precisely the accounts that most need liquidation — those between HF 1 and 1.05 under the new regime, and everything worse — are the ones that keep the old thresholds. An unprivileged borrower can also *manufacture* the condition: watch the timelocked governance operation that lowers a threshold, then borrow (permissionless up to LTV under the old stamps) so the account lands in the band, or simply let an existing position decay into it. Such debt is then shielded from liquidation while the displayed HF stays ≥ 1 on stale stamps, and eventual losses are pushed onto suppliers via `clean_bad_debt`'s supply-index write-down (contracts/controller/src/positions/liquidation/apply.rs:301-316).

### Likelihood Explanation
Medium. It requires a governance parameter change that makes a stored tuple "favor the liquidator" while an account sits in the sub-1.05 hypothetical-HF band — a recurring condition exactly when collateral risk is being tightened. No privileged action is needed by the borrower: `supply`/`borrow` under stale stamps and the permissionless nature of `update_account_threshold` mean nobody can force the restamp. The exploitation cost is just holding a position in the band.

### Recommendation
In `apply_gated_liquidation_params`, do not silently keep the old tuple for indebted accounts. Options: clamp the restamp so the stored `liquidation_threshold` moves toward the config value by the maximum amount that keeps hypothetical HF ≥ 1.05 (partial restamping); apply non-threshold components (`liquidation_bonus`, `liquidation_fees`) unconditionally since only the threshold affects the HF gate; or let `liquidate` compute eligibility against `min(stored, current)` thresholds so stale stamps cannot hide a sub-1 position.

### Proof of Concept
1. Governance lists XLM with `liquidation_threshold = 90%`. ALICE supplies 100 XLM ($1 each) and borrows $80 USDC → stored HF = 90/80 = 1.125.
2. Governance executes a ready operation lowering XLM `liquidation_threshold` to 50% (price risk).
3. Price drops XLM to $0.95. True HF = 0.5·95/80 ≈ 0.59; stale HF = 0.9·95/80 ≈ 1.07.
4. Anyone calls `update_account_threshold(caller, true, [alice_id])`. `clears_min_hf` computes HF under `LT_new` = 0.59 < 1.05 → `apply_gated_liquidation_params` returns early; the stored threshold stays 90%. Repeatable forever — the skip is a silent `return`, not a revert.
5. `liquidate(liquidator, alice_id, payments, SeizeMode::Transfer)` computes `totals.health_factor` from the stored 90% stamp → 1.07 ≥ 1 → `HealthFactorTooHigh` (plan.rs:40-44). The account is unliquidatable despite true HF 0.59.
6. Debt keeps accruing until it exceeds `0.9·C`; only then does the stale HF cross 1 and liquidation open — with the difference between `LT_new`-adjusted and `LT_old`-adjusted collateral bookable as protocol bad debt.