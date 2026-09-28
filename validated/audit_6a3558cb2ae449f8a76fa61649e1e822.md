### Title
Delisted collateral keeps its stored LTV/LT stamps and continues to back borrows and health factor after the listing is revoked - (File: contracts/controller/src/risk/totals.rs)

### Summary
CVE-2021-22264 is a stale-authorization bug: a user keeps project access after the group that granted it is deleted. The XOXNO Lending analog is stale collateral authorization: each supply position snapshots `loan_to_value`, `liquidation_threshold`, `liquidation_bonus`, and `liquidation_fees` from the spoke listing at creation, and every risk computation trusts those stored stamps rather than re-checking that the asset is still listed as collateral. When governance removes an asset from the spoke (or marks it non-collateral and the listing no longer resolves), `cached_spoke_asset` returns `None`, so both restamp paths silently skip the position and the revoked collateral keeps contributing to `ltv_collateral` and `health_factor` indefinitely.

### Finding Description
`calculate_account_risk_totals` iterates every entry in `account.supply_positions` and weights it by the *stored* `position.loan_to_value.min(position.liquidation_threshold)` and `position.liquidation_threshold` (contracts/controller/src/risk/totals.rs:190-198). No check is made that the hub asset is still listed in the account's spoke or still collateralizable.

The two refresh paths fail open the same way:
- `restamp_listed_supply_ltv` skips any `hub_asset` for which `cache.cached_spoke_asset(account.spoke_id, &hub_asset)` returns `None` (contracts/controller/src/risk/params.rs:48-50), so a removed listing is never restamped to LTV 0.
- `sync_account_thresholds` (the `update_account_threshold` keeper path) has the identical `let Some(...) else { continue }` skip (contracts/controller/src/risk/params.rs:183-185).
- Liquidation never refreshes stamps at all (documented in docs/reference/runbooks/liqvid-listing-params.md:388), so the stale threshold also protects the position from liquidation.

Net effect: an asset whose collateral privilege has been revoked still grants borrow capacity — the same "access persists after the granting entity is gone" shape as the GitLab CVE.

### Impact Explanation
A borrower can open or maintain debt backed by collateral the protocol no longer sanctions — including collateral delisted precisely because it became illiquid, manipulable, or broken. `borrow`/`withdraw` gates on `ltv_collateral`/HF computed from the stale stamps, so new borrows can be drawn against revoked collateral, and existing accounts holding only revoked collateral stay un-liquidatable under the stale LT even when the live config would make them liquidatable. Result: protocol-insolvency risk through borrows extended against delisted collateral, and delayed/unavailable liquidation of positions that should be underwater.

### Likelihood Explanation
Requires a governance listing removal or deprecation, which is an ordinary administrative operation (the codebase explicitly supports deprecated spokes and delistings, e.g. `test_update_account_threshold_syncs_deprecated_spoke_listing`). Once it happens, every pre-existing position on that asset retains its stamps automatically — no user action needed to keep the privilege. An unprivileged user reaches it via `supply` + `borrow` on a delisted-but-still-priced asset, or simply by holding a pre-existing position.

### Recommendation
On the borrow and HF paths, treat a supply position whose listing no longer resolves (or `is_collateralizable == false`) as zero weight: either drop it from `calculate_account_risk_totals`/`calculate_ltv_collateral_wad`, or stamp `loan_to_value`/`liquidation_threshold` to 0 when `cached_spoke_asset` returns `None` in `restamp_listed_supply_ltv` and `sync_account_thresholds` instead of skipping. Withdrawals should of course remain permitted.

### Proof of Concept
1. Alice `supply`s 10,000 USDC (listed, LTV 7500, LT 8000) — position stamped.
2. Governance executes `AdminOperation::EditAssetInSpoke` removing the USDC listing from the spoke (or deprecating the spoke so `get_spoke_asset` no longer resolves for the restamp paths).
3. Alice calls `borrow(ETH, …)`. `calculate_ltv_collateral_wad` still weights her USDC position by the stored `min(LTV, LT)` = 7500 (totals.rs:95-96, 190-192) and the borrow succeeds despite USDC no longer being accepted collateral.
4. Anyone calling `update_account_threshold(caller, has_risks, [alice_id])` cannot clear the stamps: `sync_account_thresholds` hits `else { continue }` for the missing listing (params.rs:183-185) and the position keeps its pre-revocation parameters.

Note: the exact storage behavior of `edit_asset_in_spoke` when `can_collateral` is cleared (whether the config entry is deleted so `get_spoke_asset` returns `None`, versus retained with `is_collateralizable = false`) was not fully verified in this pass. If the entry is retained, the restamp still ignores the collateral flag — `restamp_listed_supply_ltv` copies `config.loan_to_value` without checking `is_collateralizable` — so the stale-authorization holds in either case; only the mechanism differs.