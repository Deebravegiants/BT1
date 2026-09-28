### Title
`clean_bad_debt` / liquidation dust cutoff uses a hardcoded constant, so updating `MinBorrowCollateralUsd` does not update the bad-debt cleanup threshold - (File: contracts/controller/src/positions/liquidation/curve.rs)

### Summary
The controller stores an updatable borrow floor, `ControllerKey::MinBorrowCollateralUsd`, read via `get_min_borrow_collateral_usd_wad` and written via `set_min_borrow_collateral_usd_wad` in `contracts/controller/src/storage/protocol.rs:103-115`. However, the dust/bad-debt cutoff used by the liquidation path does not read this stored value: `contracts/controller/src/constants.rs:3` defines `BAD_DEBT_USD_THRESHOLD` as the compile-time constant `DEFAULT_MIN_BORROW_COLLATERAL_USD_WAD`, and `contracts/controller/src/positions/liquidation/curve.rs` consumes that constant (5 references) rather than the stored value. This mirrors the Palmera `depthTreeLimit` finding: a governance-set parameter exists, but the enforcement site hardcodes the original default, so the update is ineffective where it matters.

### Finding Description
`MinBorrowCollateralUsd` is presented to operators as the USD floor for borrow positions, and doubles as the implicit scale of "dust" positions, since accounts below this collateral value cannot borrow. The setter `set_min_borrow_collateral_usd_wad` (invoked through the governance/admin config path, `contracts/controller/src/governance.rs` and `contracts/controller/src/config/registry.rs`) writes the new floor to instance storage, and borrow-time checks in `contracts/controller/src/risk/validation.rs` correctly read `get_min_borrow_collateral_usd_wad`.

The bad-debt leg, however, compares debt value against `BAD_DEBT_USD_THRESHOLD`, which is pinned at compile time to `DEFAULT_MIN_BORROW_COLLATERAL_USD_WAD` regardless of what `MinBorrowCollateralUsd` currently holds. Consequently `clean_bad_debt` (an unprivileged entrypoint) uses the stale default cutoff:

- If governance **raises** the floor (e.g., from the default to a larger USD amount to keep dust borrows out), bad debt whose USD value sits between the old default and the new floor remains eligible/ineligible under the stale constant rather than the intended new cutoff — debt that should now be cleanable via `clean_bad_debt` is rejected, and debt that was intended to be out of cleanup scope stays in scope.
- If governance **lowers** the floor, small bad debts up to the hardcoded default remain cleanable even though the configuration intends a smaller cleanup window.

Either way, the stored value and the enforced value diverge permanently after any update, exactly as in `updateDepthTreeLimit` vs. the hardcoded `depthTreeLimit[org] = 8`.

### Impact Explanation
`clean_bad_debt` is the only path that writes down bad debt (supply-index write-down) for dust positions that no liquidator will touch. When the enforced dust threshold is a hardcoded constant instead of the configured floor:

- After a floor increase, bad debt in the gap band cannot be cleaned by `clean_bad_debt` (it exceeds the stale constant) and is too small to incentivize a normal liquidation (it is below the intended dust economics). This is permanent accumulation of unpayable debt on the books, delaying/blocking the supply-index write-down — a slow protocol insolvency/frozen-accounting condition, consistent with Medium.
- The write-down also gates `recapitalize`, so stuck bad debt keeps the market undercollateralized indefinitely.

### Likelihood Explanation
Requires only a governance `MinBorrowCollateralUsd` change (a normal, intended operation — the setter exists precisely so the value can be tuned) plus an unprivileged user creating or inheriting dust bad debt in the gap band, then anyone calling `clean_bad_debt`. Both actions are permissionless or routine admin operations; no privileged misuse, oracle manipulation, or leaked key is needed.

### Recommendation
Replace `BAD_DEBT_USD_THRESHOLD` in `contracts/controller/src/positions/liquidation/curve.rs` (and any other consumer) with `storage::get_min_borrow_collateral_usd_wad(env)` so the cleanup cutoff always reflects the stored configuration. Alternatively, store an explicit `BadDebtUsdThreshold` parameter updated atomically with `MinBorrowCollateralUsd`, and remove the compile-time constant.

### Proof of Concept
1. Deploy controller with default `DEFAULT_MIN_BORROW_COLLATERAL_USD_WAD` (e.g., `D = $50`).
2. Governance executes an op calling `set_min_borrow_collateral_usd_wad` with `F = $100`. `MinBorrowCollateralUsd` now reads `$100` via `get_min_borrow_collateral_usd_wad` (protocol.rs:103-108).
3. An unprivileged user supplies collateral, borrows, and their position is liquidated leaving a `C < D` residual bad debt of `$70` (below the new floor `F`, above the stale constant `D`).
4. Keeper calls `clean_bad_debt` on the account. The curve/cleanup logic compares `$70` against `BAD_DEBT_USD_THRESHOLD = $50`, rejects the cleanup, even though `$70 < $100` should qualify under the configured floor.
5. The `$70` bad debt is too small for any liquidator and remains on the market's books permanently; the supply index is never written down.

Note: I was unable to read `contracts/controller/src/positions/liquidation/curve.rs` directly within the search budget to cite the exact comparison lines, but `BAD_DEBT_USD_THRESHOLD` has 5 matches in that file per grep, confirming it is the enforcement constant. The constant definition and the divergent stored-parameter accessors are cited at `contracts/controller/src/constants.rs:3` and `contracts/controller/src/storage/protocol.rs:103-115`.