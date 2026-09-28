### Title
Permissionless ordering of concurrently-Ready timelock ops lets any address pick the final admin parameter value - (File: contracts/governance/src/api.rs)

### Summary
`Governance::execute` / `execute_self` accept `executor: Option<Address>`; when `None`, no executor role check runs — anyone may drive any Ready op (`api.rs:53-67`). Ops are keyed by `(target, function, args, predecessor, salt)` and `predecessor` is always 32 zero bytes (`contracts/governance/README.md:15`), so nothing chains or supersedes ops: two ops writing the same controller slot can both be `Ready` at once, and an unprivileged caller chooses which one lands last. The bug class is identical to the `isValidHash` mapping in the report — multiple live authorizations, final state decided by permissionless call order. The codebase already applies the report's recommended fix pattern to exactly one op (`RelaxSpokeAssetFlags` is bound to a per-listing flags epoch and reverts `SpokeFlagsEpochMismatch` if any flag write lands first — README `:37-45`), leaving every other parameter op exposed.

### Finding Description
- `lifecycle::execute` is invoked with the caller-supplied `Option<Address>` executor and only requires auth/EXECUTOR role when `Some` (`api.rs:57-67`).
- `propose` returns an id derived from the op contents plus a fresh `salt`; there is no "latest proposal wins" or per-target nonce — `predecessor` is always zero (README `:15`), so N ops on the same knob coexist in `Ready`.
- Ops that can overlap include `AdminOperation::SetMinBorrowCollateralUsd`, `SetPositionLimits`, `EditAssetInSpoke` (LTV/threshold/caps for a listing), `SetSpokeLiquidationCurve`, oracle tolerance edits, and `Unpause`. The test suite itself shows two different `SetPositionLimits` values scheduled concurrently (`tests/integration/flows/governance.sh:82-95`).
- Execution order is therefore attacker-chosen: submit op B (newer value), then op A (older value) — final state = A, contradicting the proposer's latest intent. The one knob that *is* protected proves the fix shape: `RelaxSpokeAssetFlags` carries `expected_epoch` and reverts on intervening writes.

### Impact Explanation
Medium. An unprivileged address can pin a superseded admin parameter as the live config — e.g., land an older `EditAssetInSpoke` with a higher LTV/liquidation threshold after governance already scheduled tighter risk parameters, or land a stale `SetMinBorrowCollateralUsd` floor. Depending on the stale values this enables borrows the current governance intent would forbid (insolvency path) or keeps a weaker liquidation curve/bonus active (losses absorbed by suppliers). Both values were proposer-intended at some point, which caps this at Medium rather than High — matching the severity of the source finding.

### Likelihood Explanation
Requires two ops on the same slot to be `Ready` simultaneously. That is routine whenever governance re-proposes a parameter change (the ops tooling even supports `REAPPLY_ON_DONE`/`SALT_NONCE` re-proposals and batch `executeReady`, and an expired op "stays scheduled" per `permissionless_execution.rs:124-127`, widening the overlap window). Once overlapped, ordering is trivially controllable by any caller since `executor=None` requires no role or signature.

### Recommendation
Apply the epoch/nonce pattern already used for `RelaxSpokeAssetFlags` to all parameter-writing ops: store a per-target/per-listing config epoch on the controller, embed `expected_epoch` in each `AdminOperation`, and revert at execution when the stored epoch has advanced — equivalently, record a single "current pending op id" per target so a newer proposal supersedes the old one (the report's `bountyHash` recommendation).

### Proof of Concept
1. Proposer schedules `SetMinBorrowCollateralUsd(50e18)` (op A) and later `SetMinBorrowCollateralUsd(5e18)` is deemed wrong; or in the attack direction, governance proposes tighten `EditAssetInSpoke` (op B) while an older looser `EditAssetInSpoke` (op A) is still `Ready`.
2. Attacker waits until both A and B are `Ready` (any overlap during the `GRACE` window; expired ops stay `Ready`-scheduled).
3. Attacker calls `execute(None, controller, "edit_asset_in_spoke", argsB, 0, saltB)` then `execute(None, controller, "edit_asset_in_spoke", argsA, 0, saltA)`.
4. Controller state ends at op A's stale parameters — the weaker LTV/threshold governance had already superseded — purely because a permissionless caller chose the order.