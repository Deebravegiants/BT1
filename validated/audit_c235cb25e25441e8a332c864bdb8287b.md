Let me confirm the no_seize seizure-blocking code path.### Title
Borrower bricks their own liquidation by supplying a `no_seize`-listed asset — protocol-wide forced sale can be cancelled at will - (File: contracts/controller/src/positions/liquidation/plan.rs)

### Summary
Analogous to the OSDA market owner closing the market to avoid a low-price sale, an unprivileged XOXNO Lending borrower can veto the forced sale of their collateral. The liquidation plan seizes collateral pro-rata across **all** supply legs of the account, and `enforce_spoke_asset_flags(.., FreezePolicy::SeizureLeg)` reverts the entire call if any seized leg's listing carries `no_seize`. Because `no_seize` does not block entry (only `paused`/`frozen` do), an account owner can supply even a dust amount of a `no_seize`-flagged listed asset into their own account and make every subsequent `liquidate` call revert — even if the asset was supplied after the flag was set (explicitly documented behavior, INV-HALT-02).

### Finding Description
- `build_liquidation_plan` computes `seized_collaterals` pro-rata over all supply positions, then runs the seizure-leg flag check for each; a single `no_seize` leg panics the whole transaction (`contracts/controller/src/positions/liquidation/plan.rs:73-89`). There is no mechanism to drop or skip a `no_seize` leg — zero-amount legs are omitted, but any nonzero balance on a `no_seize` listing bricks the call.
- `supply` is permissionless for the account owner/delegate; `no_seize` is not checked on entry (INV-HALT-02: "entry rejects `paused` and `frozen`"; only seizure rejects `no_seize`). The owner can open a new asset slot and deposit dust.
- Flags ratchet only tighter via `set_spoke_asset_flags`/`edit_asset_in_spoke` (`contracts/controller/src/config/asset.rs:175-186`); clearing `no_seize` requires the timelocked, epoch-bound `relax_spoke_asset_flags`, so the borrower can keep the shield up until governance executes a relaxation — and can simply re-supply the leg each time it is relaxed and their balance was seized... the shield persists as long as the balance is nonzero.
- `clean_bad_debt` bypasses the flags, but only once collateral value ≤ the $5 dust threshold — all value above dust remains unliquidatable, i.e. the borrower avoids the collateral sale entirely for large positions.

### Impact Explanation
While any collateral leg sits on a `no_seize` listing, no liquidator can repay that account's debt — every `liquidate` reverts during plan construction. The borrower thereby "closes the market" on their own forced sale, exactly the bug class of the report. If the position is or becomes undercollateralized, interest keeps accruing and the shortfall eventually lands on suppliers via `clean_bad_debt`/`force_socialize_bad_debt` supply-index write-down — protocol insolvency absorbed by innocent suppliers, while the borrower retains both the borrowed funds and their collateral.

### Likelihood Explanation
Requires a `no_seize`-flagged listing in the account's spoke — a real (governance-set, ratcheted) state used for assets whose seizure is unsafe. Once such a flag exists, the attack needs only one `supply(caller=owner, account_id, spoke_id, assets=[(no_seize_asset, dust)])`. It is cheap, repeatable, and needs no price manipulation, timing, or privileged access.

### Recommendation
Skip `no_seize` legs in `calculate_seized_collateral` and exclude their value from the pro-rata base (seize only from seizable collateral), instead of reverting the whole plan. Alternatively, treat supplying a `no_seize` asset as `frozen`-equivalent for accounts with outstanding debt, or cap liquidation-seizure blocking to legs that existed before the flag was set.

### Proof of Concept
1. Governance (or a GUARDIAN immediate op) sets `no_seize` on asset X in spoke S — a legitimate flag tightening.
2. Borrower B supplies collateral C in spoke S, borrows D.
3. Price moves; B's HF drops below 1. Liquidator calls `liquidate(liquidator, B, [(debt_asset, amt)], SeizeMode::Transfer)` — succeeds normally.
4. B calls `supply(B, account_id, S, [(X, 1)])` — accepted, since `no_seize` does not gate entry.
5. Every subsequent `liquidate` on B reverts at the `FreezePolicy::SeizureLeg` check in `build_liquidation_plan` because the pro-rata seizure plan now includes the nonzero X leg.
6. B's debt accrues interest unliquidatable until governance timelock-relaxes `no_seize` or B's collateral decays to ≤ $5 dust, at which point the residual debt is socialized onto suppliers via `clean_bad_debt`.