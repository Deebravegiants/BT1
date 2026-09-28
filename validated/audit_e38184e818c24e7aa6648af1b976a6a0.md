### Title
Front-running `supply`/`borrow` with dust can permanently block victims at a near-full spoke cap - (File: contracts/controller/src/spoke_usage.rs)

### Summary
`SpokeUsageContext::apply_entry` enforces supply and borrow caps by reverting (`SpokeSupplyCapReached` / `SpokeBorrowCapReached`) whenever `usage_scaled + delta_scaled > cap_scaled`, instead of clamping the accepted amount to the remaining headroom. When a spoke's `supply_cap` (or `borrow_cap`) is nearly exhausted, an unprivileged attacker can repeatedly front-run a victim's `supply` call with a dust deposit of a few base units, causing the victim's transaction to revert. This mirrors the JUSDBank `_deposit` cap-check-after-transfer issue, mapped onto XOXNO Lending's scaled-share cap accounting.

### Finding Description
`enforce_spoke_cap` (contracts/controller/src/spoke_usage.rs:144-157) computes `cap_scaled = calculate_scaled_cap(cap, decimals, index)` and asserts `next_scaled <= cap_scaled`, reverting the whole transaction with `SpokeError::SpokeSupplyCapReached` (#311) or `SpokeBorrowCapReached` (#312). There is no code path that reduces `delta` to fit the remaining headroom — the check is all-or-nothing. This is confirmed by tests such as `test_supply_of_exactly_the_cap_succeeds_then_one_unit_reverts` (tests/test-harness/tests/controller/spoke_caps.rs:338-355) and `apply_entry_one_over_cap_reverts_with_supply_cap` (contracts/controller/tests/spoke.rs:265-284), which pin the revert-not-clamp behavior.

Because the cap is a shared per-(spoke, hub_asset) resource tracked in `SpokeUsageRaw.supplied_scaled_ray` / `borrowed_scaled_ray`, any account can consume the final sliver of headroom. An attacker monitoring pending transactions sees a victim's `supply(account, spoke_id, payments)` where `payments` is sized to use the last available capacity; the attacker first submits their own `supply` of e.g. 1-10 base units on the same key, pushing `usage` to the cap. The victim's transaction then reverts with #311. Each time the victim retries with a slightly smaller amount, the attacker tops off the cap again. The attacker's cost is only the dust amount supplied (which they retain as a real position and can later `withdraw`, since exits consume no cap), plus fees.

### Impact Explanation
Temporary freezing of funds / griefing DoS: the victim's collateral deposit is repeatedly reverted, so their funds are unusable in the protocol for as long as the attacker keeps saturating the cap. For borrowers, the same applies to `borrow` when `borrow_cap` is nearly reached — e.g., a user trying to borrow to avert liquidation can be blocked from drawing the remaining cap headroom. The attacker loses almost nothing: dust supplied stays withdrawable (exits bypass caps), and dust borrowed is just ordinary debt. The attack requires no privileges and works on any spoke with a configured cap approaching utilization.

### Likelihood Explanation
Medium likelihood conditioned on market configuration: it only applies when a spoke cap is within a small margin of being full and a targeted transaction is visible in flight. Caps are real, enforced configuration in this codebase (`SpokeAssetConfig.supply_cap`/`borrow_cap`), and mainnet configs set finite caps, so the near-cap regime does occur. Stellar/Soroban transaction submission gives an attacker a window to land a competing transaction first. The attack costs little gas and requires no capital beyond dust.

### Recommendation
In `apply_entry`/`enforce_spoke_cap` (or at the supply/borrow call sites in `contracts/controller/src/lib.rs`), clamp `delta_scaled` to `min(delta_scaled, cap_scaled - usage_scaled)` before booking usage, and derive the actual token amount from the clamped scaled value (respecting floor/ceil unscaling in `contracts/pool/src/scale.rs`) so the user deposits/borrows only up to remaining headroom rather than reverting. Alternatively, document that callers must query headroom off-chain and accept the revert — but the revert-not-clamp design remains front-runnable, so clamping at entry is the robust fix.

### Proof of Concept
Using the existing harness pattern (tests/test-harness/tests/controller/spoke_caps.rs):
1. `set_spoke_caps(&t, 2, "USDC", 1_000 * UNIT, UNCONSTRAINED_TEST_CAP)` — supply cap of 1,000 USDC.
2. Victim supplies `999 * UNIT`, leaving `1 * UNIT` of headroom, then prepares `supply` of `1 * UNIT` to fill the cap.
3. Attacker front-runs with `try_supply_raw(ATTACKER, "USDC", 1)` — a 1-base-unit supply that pushes `supplied_scaled_ray` to the cap boundary.
4. Victim's `supply` of `1 * UNIT` now reverts with `SPOKE_SUPPLY_CAP_REACHED` (#311), exactly as `test_supply_of_exactly_the_cap_succeeds_then_one_unit_reverts` demonstrates.
5. Each time the victim retries with a reduced amount, the attacker supplies dust again; the victim's funds remain outside the protocol until the cap is raised by governance or the attacker stops. The same sequence holds against `borrow` with `borrow_cap`, per `test_spoke_borrow_cap_enforced` (tests/test-harness/tests/controller/spoke.rs:752-776).