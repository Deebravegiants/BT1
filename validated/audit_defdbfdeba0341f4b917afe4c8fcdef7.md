### Title
Third-party `supply` force-restamps a foreign account's liquidation parameters without an aggregate health-factor gate - ([File: contracts/controller/src/positions/supply.rs])

### Summary
The Mattermost bug class — an unprivileged caller mutating another party's resource because a permission check was missing — maps onto XOXNO Lending's third-party supply path. Any authenticated address may call `supply` on a foreign `account_id` for a market the account already supplies (INV-AUTH-03). The merge leg then restamps the victim's cached liquidation tuple (`liquidation_threshold`, `liquidation_bonus`, `liquidation_fees`) at `RiskRefreshScope::FullTuple`, gated only by a per-position hypothetical HF ≥ 1.05 check — unlike the keeper path `update_account_threshold`, which re-checks the *final* aggregate HF ≥ 1.05 after all positions are restamped.

### Finding Description
`process_supply` admits any `caller` when every supplied `hub_asset` already exists in the victim's `supply_positions` — `require_third_party_existing_supply` only asserts slot existence, never ownership (`contracts/controller/src/positions/supply.rs:86-97`). Each leg flows through `merge_supply_leg`, which calls `refresh_supply_risk_params(..., RiskRefreshScope::FullTuple)` (`supply.rs:288-296`). That applies `apply_gated_liquidation_params`, which skips a harmful restamp only when `clears_min_hf` fails — and `clears_min_hf` evaluates the health factor with **only that single position's** threshold replaced (`risk/params.rs:103-119`).

By contrast, the intended permissionless restamp path `update_account_threshold` → `sync_account_thresholds` recomputes the account's aggregate HF *after* every position has been updated and reverts below 1.05 (`risk/params.rs:221-234`). The supply path has no equivalent post-merge check — ordinary `supply` deliberately skips solvency checks (docs/reference/endpoints.md:55).

### Impact Explanation
After governance lowers a liquidation threshold (or raises the bonus / cuts the fee) on multiple markets, an attacker can push a victim below HF 1 by dust-supplying each existing market. Each leg's `clears_min_hf` sees only its own restamp (e.g., HF ≈ 1.06 each), yet the combined restamp leaves the account at HF < 1 — a state `update_account_threshold` itself could not produce. The attacker then immediately calls `liquidate` on the now-underwater account and extracts the liquidation bonus via `SeizeMode::Transfer` or `Credit(0)`. The victim loses collateral to the bonus and fees that the still-stamped old parameters would have prevented.

### Likelihood Explanation
Requires a governance parameter change that is harmful per-position but individually passes the 1.05 gate — a routine occurrence on any multi-collateral account when listings are tightened. The attacker needs only dust of each already-held collateral asset and can atomically supply, then liquidate. `favors_liquidator` (`risk/params.rs:96-100`) confirms the harmful direction is exactly what the gate is meant to control, and the missing aggregate check makes the bypass deterministic once preconditioned.

### Recommendation
In `process_supply`/`merge_supply_leg`, either downgrade third-party merges to `RiskRefreshScope::LtvOnly` (a non-owner should never alter a foreign account's liquidation terms — mirroring the "cannot open a foreign asset slot" spirit of INV-AUTH-03), or, after `process_deposit`, recompute the aggregate health factor and assert `hf >= THRESHOLD_UPDATE_MIN_HF_RAW` whenever any leg applied a tuple restamp to an account the caller does not own, matching `sync_account_thresholds`.

### Proof of Concept
1. Governance lowers `liquidation_threshold` on USDC and ETH from e.g. 9,700 → 8,000 bps.
2. Victim account supplies USDC and ETH, borrows against them; HF = 1.20 with old stamps. With both restamped, HF = 0.98; with only one restamped, HF = 1.06.
3. Attacker calls `supply(caller=attacker, account_id=victim, assets=[(USDC, 1), (ETH, 1)])`. `require_third_party_existing_supply` passes (both slots exist); each `merge_supply_leg` restamps because each `clears_min_hf` individually returns true.
4. Account HF is now 0.98. Attacker calls `liquidate` and seizes collateral with bonus — a liquidation the gated keeper path would have refused to enable.

Note: the exact HF arithmetic depends on accrued indexes and prices; the structural gap (per-position gate vs. missing aggregate gate, present on `update_account_threshold` but absent on `supply`) is directly visible in `risk/params.rs:103-119` vs. `risk/params.rs:221-234` and `supply.rs:288-296`.