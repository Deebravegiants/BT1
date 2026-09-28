### Title
Disabling collateral via `is_collateralizable = false` does not stop it from backing new borrows - (File: contracts/controller/src/risk/totals.rs)

### Summary
The spoke flag `is_collateralizable` is only enforced on the supply entry path (`require_can_supply`), mirroring the Papr bug where `isAllowed` was only checked in `addCollateral`. Once a user holds a supply position, the risk engine keeps valuing it with its stored LTV and liquidation threshold even after governance disables the asset as collateral, so the user can keep minting debt against a disabled collateral via `borrow`, `multiply`, or `flash_position`.

### Finding Description
`validate_position_entry_gates` in `contracts/controller/src/positions/mod.rs:243-252` checks `require_can_supply` for `Deposit` legs and `require_can_borrow` for `Borrow` legs. `require_can_borrow` (`mod.rs:201-213`) asserts `is_borrowable` on the debt asset only — it never re-validates `is_collateralizable` on the account's existing supply positions.

Solvency after a borrow is enforced by `enforce_post_pool_solvency` → `calculate_account_risk_totals` (`contracts/controller/src/risk/totals.rs:157-216`), which weights every supply position by its stored `min(loan_to_value, liquidation_threshold)` and `liquidation_threshold`. These snapshots live on the `AccountPosition` and are unaffected by the collateral flag.

`restamp_listed_supply_ltv` (`contracts/controller/src/risk/params.rs:44-64`) refreshes LTV from the current spoke config for still-listed assets, but `edit_asset_in_spoke` with `can_collateral = false` does not force `ltv`/`threshold` to zero — `SpokeAssetArgs` carries them as independent fields (`common/src/types/controller.rs:128-149`). The integration test `test_spoke_collateral_flag_update_blocks_new_supply_but_existing_withdraw_works` (`tests/test-harness/tests/controller/spoke.rs:580-605`) confirms the intended semantics: flag-off blocks only *new supply*; the existing position (and therefore its collateral weight) is untouched.

Net effect: a user supplies asset X while it is collateral-enabled, governance later sets `can_collateral = false` (e.g., the asset is being deprecated for risk reasons), and the user can still call `borrow(spoke_id, debt_asset, amount)` — the borrow gate only checks the debt asset's `is_borrowable`, and the HF check still credits the disabled collateral at full stored LTV.

### Impact Explanation
Protocol insolvency risk: an asset governance has deliberately excluded from collateral (typically because its price feed or liquidity is no longer trusted) continues to back freshly minted debt. If the flag is disabled precisely because the asset's valuation is unreliable, new borrows against it can leave the pool undercollateralized — the exact impact class of the Papr M-02 report.

### Likelihood Explanation
Medium. Requires a privileged `edit_asset_in_spoke` call disabling collateral, which is a routine risk action. After that, any unprivileged holder of the asset can borrow against it at full LTV — the disabled flag provides zero protection on the debt-minting side.

### Recommendation
On `borrow`/`multiply`/`flash_position` (and in `restamp_listed_supply_ltv`), treat supply positions whose current spoke config has `is_collateralizable = false` as zero-weight for `ltv_collateral` and `weighted_collateral`, or force `ltv`/`threshold` to zero in the position snapshot when the flag is cleared. Alternatively, document and enforce that disabling collateral must always be paired with `ltv = 0`, `threshold = 0` in `edit_asset_in_spoke`.

### Proof of Concept
```rust
// Harness-level PoC sketch (same shape as spoke.rs:580-605)
let mut t = LendingTest::new().stablecoin_spoke_two_asset().build();
t.create_spoke_account(ALICE, 2);
t.supply(ALICE, "USDC", 10_000.0);

// Governance disables USDC as collateral (keeps ltv/threshold unchanged)
t.edit_asset_in_spoke("USDC", 2, false, true, 9700, 9800, 200);

// Alice can still borrow USDT against the now-disabled USDC collateral;
// calculate_account_risk_totals credits the stored LTV/threshold.
let borrow = t.try_borrow(ALICE, "USDT", 5_000.0);
assert!(borrow.is_ok(), "BUG: disabled collateral still backs new debt");
```

Confidence caveats: I did not fully trace `process_borrow` in `debt.rs` to confirm no additional per-collateral flag check exists downstream of `validate_position_entry_gates`, nor `update_or_remove_supply_position`'s removal condition, so there is a small chance a later gate re-checks `is_collateralizable`. Based on `mod.rs`, `totals.rs`, and the existing flag tests, the disabled-collateral-still-backs-debt behavior appears to be reachable by any unprivileged account holding the asset.