### Title
An unprivileged user can permanently block `remove_asset_from_spoke` by keeping a dust position in the target spoke — (File: contracts/controller/src/config/asset.rs)

### Summary
The owner-only `remove_asset_from_spoke` entrypoint (executed via the timelocked `AdminOperation::RemoveAssetFromSpoke`) reverts with `SpokeAssetInUse` whenever the spoke's aggregate scaled supply or borrow for that asset is nonzero. Because this check is evaluated at execution time and usage is user-controllable, a single unprivileged address can keep a trivial dust position alive in that spoke and make every removal attempt fail — permanently preventing governance from delisting the asset. This mirrors the reported bug class: a user-controllable "pending state" check inside an admin action that the affected party can perpetually satisfy to block the admin.

### Finding Description
`remove_asset_from_spoke` in `contracts/controller/src/config/asset.rs:190-211` asserts `usage.supplied_scaled_ray == 0 && usage.borrowed_scaled_ray == 0` before deleting the listing. The function is reachable only through governance: `remove_asset_from_spoke` is `#[only_owner]` on the controller (`contracts/controller/src/lib.rs:712-719`), and the controller owner is the governance contract, which executes it via `Governance::execute` after the timelock delay (`contracts/governance/src/api.rs:53-67`).

Two properties make the check griefable:

1. **The check is evaluated at execution, not at proposal.** The attacker does not even need a mempool race: a `RemoveAssetFromSpoke` op sits in `Waiting` for the full min-delay, giving the attacker a large window to call `supply` with a dust amount in that spoke before `execute` runs.
2. **Dust usage is enough.** Any positive scaled amount keeps `supplied_scaled_ray > 0`. There is no minimum supply threshold gating the check — a position worth fractions of a cent permanently fails `SpokeAssetInUse`.

Governance mitigations do not close the hole:

- Setting `paused`/`frozen` via the guardian ratchet (`set_spoke_asset_flags`, `asset.rs:112-124`) blocks new supply/borrow entry, but does not clear usage already created — the attacker can supply dust the moment the asset is listed or the moment the removal op is proposed, before any freeze lands.
- Even under `frozen`, Credit-mode liquidation credits seized supply shares to a same-spoke receiver, and seizure rejects only `no_seize`, not `frozen` (INV-HALT-02; `docs/explanation/threat-model.md`). An attacker can manufacture a fresh supply position in the spoke via a self-liquidation in Credit mode to re-poison the check.
- Caps of zero stop growth but cannot remove existing usage; there is no forceful position eviction.

Each failed execution requires governance to re-propose and wait the full timelock again, while the attacker only needs to keep dust parked.

### Impact Explanation
Governance loses the ability to delist an asset from a spoke. This matters operationally when a listing must be removed — e.g., an asset whose oracle or market is being decommissioned, or a listing added in error. The listing remains live (or at best frozen with zero caps, which still leaves it enumerated and forces usage-bearing users to keep stale config), and the admin function is permanently DoS'd by a single unprivileged address at negligible cost. This is a persistent denial of a protocol administration function driven entirely by user-reachable state, analogous to permanently blocking `deauthorizeAccount`.

### Likelihood Explanation
High likelihood of the condition being reachable: any address can call `supply` on a live listing, the cost is a dust amount plus transaction fees, and the timelock delay guarantees a large reaction window. No privileged role, oracle manipulation, or flash loan is required. The severity is bounded because caps and flags can still neutralize new risk on the listing, so this is a Medium.

### Recommendation
Mirror the report's recommendation: remove the strict zero-usage gate, or make it non-blocking for the attacker:

1. On `remove_asset_from_spoke`, either (a) force-close or socialize remaining dust positions below a USD threshold (as `clean_bad_debt` does for insolvent accounts), or (b) skip/zero the dust gate and mark the listing removed while leaving existing positions settle-only under a deprecated-listing path, the same way `remove_spoke` already "deprecates" a spoke without an empty-spoke check (`contracts/controller/src/config/spoke.rs:38-49`).
2. Alternatively, compare usage against a protocol-defined dust floor (`supplied_scaled_ray * index <= DUST_USD`) rather than exact zero, so a dust attack cannot satisfy the gate.
3. Audit every other admin/timelocked operation for execution-time checks satisfiable by unprivileged state changes (front-runnable gates), per the report's long-term recommendation.

### Proof of Concept
1. Governance lists `hub_asset = (hub_id, USDC)` in `spoke_id = S`. Attacker Eve calls `controller.supply(caller=Eve, account_id=0, spoke_id=S, asset=USDC, amount=1)` (1 base unit), creating `spoke_usage[S][hub_asset].supplied_scaled_ray > 0`.
2. Governance proposes `AdminOperation::RemoveAssetFromSpoke{hub_asset, spoke_id:S}`; the op becomes `Ready` after `get_min_delay` ledgers.
3. Anyone calls `Governance::execute(..., target=controller, function="remove_asset_from_spoke", ...)`. The call reaches `remove_asset_from_spoke`, reads `get_spoke_usage` with `supplied_scaled_ray > 0`, and panics with `SpokeAssetInUse` (`asset.rs:196-201`).
4. The guardian tightens `frozen=true`; Eve's existing dust position still holds usage > 0. Every subsequent removal attempt reverts. If usage were somehow cleared, Eve re-poisons it via a Credit-mode self-liquidation crediting a USDC supply position in spoke `S` (seizure is not gated by `frozen`), restoring `supplied_scaled_ray > 0` before the next `execute`.

Result: the listing can never be removed while Eve maintains the dust position; governance is permanently blocked at trivial cost.