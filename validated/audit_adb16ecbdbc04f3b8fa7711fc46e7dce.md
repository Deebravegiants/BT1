### Title
Stale `EditAssetInSpoke` snapshots overwrite newer listing risk parameters — only halt flags carry a freshness epoch - (File: contracts/controller/src/config/asset.rs)

### Summary
The ClearanceKit bug class is "an older legitimately-authorized snapshot is accepted because the verifier binds no version/freshness counter." XOXNO Lending reproduces this shape in the governance → controller listing-edit path: `AdminOperation::EditAssetInSpoke` captures a full `SpokeAssetArgs` snapshot at proposal time, and `upsert_spoke_asset` writes that entire snapshot unconditionally. A monotonic counter (`SpokeFlagsEpoch`) exists, but it guards only the `paused`/`frozen`/`no_seize` trio via `relax_spoke_asset_flags` and the flag ratchet. Every other field in the listing — `loan_to_value`, `liquidation_threshold`, `liquidation_bonus`, `liquidation_fees`, `supply_cap`, `borrow_cap`, `can_collateral`, `can_borrow` — is clobbered by the stale payload with no epoch check, and execution is permissionless (`execute(executor: None, ...)`), so any unprivileged address can land the stale snapshot once the delay elapses.

### Finding Description
`edit_asset_in_spoke` calls `upsert_spoke_asset(.., Edit)`, which enforces `require_flag_ratchet` (flags may only tighten) and then stores the complete `SpokeAssetConfig` built from the arguments — the state as it was captured when the operation was proposed, not as it is at execution time (contracts/controller/src/config/asset.rs:29-92). The flags epoch (`bump_spoke_flags_epoch`) is advanced only when flag bits change, and is consulted only by `relax_spoke_asset_flags` (contracts/controller/src/config/asset.rs:129-145, 93-95). Nothing versions LTV/LT/bonus/caps.

The repository's own tests acknowledge the asymmetry: `stale_edit_executed_by_a_stranger_cannot_clear_a_guardian_freeze` proves a stale edit cannot clear a *flag*, but the same stale op would happily regress the other fields — e.g., overwrite a newer, deliberately tightened `loan_to_value`, `liquidation_threshold`, or `supply_cap` produced by a later executed op or a later guardian-era reconfiguration. The runbook even directs operators to "cancel each Waiting or Ready operation" during incidents because pending edits are stale snapshots (docs/reference/runbooks/freeze-a-listing.md:26-38) — the on-chain defense exists only for flags.

Concretely, an attacker path an unprivileged address can submit:

1. Governance schedules `EditAssetInSpoke(A)` with the then-current permissive parameters (e.g., `supply_cap = 1e9`, `ltv = 8000`). It reaches `Ready`.
2. A later executed op tightens the listing (`EditAssetInSpoke(B)` with `supply_cap = 0` or a lower LT/LTV to wind the market down), or the risk situation changed making A's parameters unsafe.
3. Any stranger calls `governance.execute(None, controller, "edit_asset_in_spoke", argsA, predecessor, salt)` — in the allowed surface — and the stale snapshot silently overwrites B's tighter values because only flags are epoch-guarded (contracts/governance/src/timelock/lifecycle.rs:85-109; contracts/controller/src/config/asset.rs:60-95).

### Impact Explanation
A stale edit restores outdated risk parameters on a live listing. Reinstating an old high `supply_cap`/`borrow_cap` after governance capped the market reopens entry the protocol intended closed; restoring a stale higher `liquidation_threshold`/`loan_to_value` after a tightening lets new borrows exceed intended limits — direct protocol-insolvency surface. Conversely a stale *harsher* snapshot (lower LT/bonus written before a later relief edit) restamps parameters users borrowed under, exposing existing positions to unintended liquidation terms via `update_account_threshold`/`merge_supply_leg` restamping. This maps to theft of user funds / protocol insolvency and matches the CVE's "older signed snapshot accepted as fully valid" shape: the args were legitimately proposed and verified (op-id hash), but carry no freshness binding to listing evolution.

### Likelihood Explanation
Medium-low but real: it requires a superseded `EditAssetInSpoke` to remain in `Ready` state (operations stay executable until the grace window expires, and a canceller may miss it) plus an interleaved newer write to the same listing — exactly the incident/wind-down scenario the runbook anticipates. The trigger is fully permissionless and the revert conditions cover only flag-clearing, so the stale non-flag fields land without error.

### Recommendation
Bind `EditAssetInSpoke` (and `AddAssetToSpoke` where a listing could already exist) to the listing's configuration epoch: either extend `SpokeFlagsEpoch` semantics to a full config epoch bumped on every `upsert_spoke_asset`, or add an `expected_config_epoch`/`expected_config_hash` to `SpokeAssetArgs` validated in `upsert_spoke_asset` the same way `expected_epoch` is validated in `relax_spoke_asset_flags` — rejecting any edit whose snapshot predates a newer committed write. Alternatively, make `EditAssetInSpoke` carry per-field ratchets (caps may only tighten pending ops, matching the flag ratchet).

### Proof of Concept
```rust
// tests/test-harness/tests/governance/stale_edit_and_sensitive_floor.rs pattern:
// 1. Read live listing cfg (ltv=8000, supply_cap=C0, no flags set).
// 2. gov.propose(admin, EditAssetInSpoke(args_A)) where args_A keeps flags
//    false/false/false and ltv=8000, supply_cap=C0  -> op A, Waiting.
// 3. Advance delay; execute a SECOND scheduled op B that tightens the listing:
//    ltv=5000, threshold=6000, supply_cap=0. Listing now B.
// 4. Advance ledger so op A is Ready. A stranger calls
//    gov.execute(None, controller, "edit_asset_in_spoke", args_A, pred, salt).
// 5. execute succeeds (require_flag_ratchet passes: flags unchanged);
//    assert get_spoke_asset(...) == args_A  // stale ltv=8000/cap=C0 silently
//    overwrote B's tighter values. No epoch check rejected it.
```
The existing unit test scaffolding (`upsert_spoke_asset`, `relax_*` epoch tests in contracts/controller/tests/config/asset_flags.rs) shows the guard exists for flags and is absent for every other `SpokeAssetConfig` field.