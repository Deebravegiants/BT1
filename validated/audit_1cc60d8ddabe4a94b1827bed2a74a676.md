### Title
Permissionless `update_account_threshold` lets any address downgrade a victim's cached LTV and freeze their withdrawals/borrows - ([File: contracts/controller/src/risk/params.rs](contracts/controller/src/risk/params.rs))

### Summary
The Fleet advisory is broken access control: an endpoint reachable by low-privilege users that should have been role-gated. The analog is `controller::update_account_threshold`. It is permissionless by design, and the liquidation tuple is protected by an HF >= 1.05 gate — but the LTV restamp is not gated at all. Since LTV, not the liquidation threshold, feeds the solvency check on `withdraw` and `borrow`, any unprivileged address can force a victim's stored LTV down to a newly listed lower value and make their withdrawals revert, temporarily freezing their collateral.

### Finding Description
`update_account_threshold` requires only `caller.require_auth()` — any address may invoke it on arbitrary `account_ids` (`risk/params.rs:124-130`). With `has_risks = false` it runs `RiskRefreshScope::LtvOnly`. In `refresh_supply_risk_params`, `position.loan_to_value = effective_config.loan_to_value` is applied unconditionally (`params.rs:35`), while the liquidation tuple path (`apply_gated_liquidation_params`, `params.rs:68-93`) is the only one guarded by the HF >= 1.05 check and the `favors_liquidator` comparison. The final HF assertion in `sync_account_thresholds` (`params.rs:221-234`) only runs under `FullTuple`, so the `LtvOnly` path performs no solvency check whatsoever.

The declared invariant (`scripts/permissionless_entrypoints.txt`, `controller::update_account_threshold`) justifies this by stating "restamps LTV only, which the health factor does not read." That reasoning misses the second consumer of LTV: per the endpoint reference, `borrow` and `withdraw` require LTV-weighted collateral to cover debt. A victim account opened under LTV 80% whose market is later listed at LTV 50% keeps the stale 80% snapshot until someone restamps it. The owner can still withdraw because HF (threshold-based) is fine and the cached LTV still passes the post-withdraw LTV check — but once any stranger calls `update_account_threshold(caller, false, [victim_id])`, every supply position's LTV is rewritten to 50%, the LTV-weighted coverage fails, and `withdraw`/`borrow` revert. Governance raising the LTV back, or the victim repaying enough debt, is required to unlock funds.

### Impact Explanation
Temporary freezing of funds: a single unprivileged transaction permanently applies the listed LTV to a victim account, after which the victim's `withdraw` and `borrow` calls revert until debt is reduced enough to satisfy the lower LTV or governance raises LTV again. Unlike the liquidation-tuple refresh, there is no HF floor protecting the victim.

### Likelihood Explanation
Medium. The attack is permissionless, costs one call, and can hit many accounts in a single `account_ids` vector (griefing the whole book). However, it is conditional on governance having lowered a market's listed LTV after the victims supplied — it weaponizes a legitimate parameter change rather than creating harm standalone. No funds are stolen, and the freeze is reversible, capping severity at Medium.

### Recommendation
Apply the same protection the liquidation tuple enjoys to the LTV restamp: either gate `LtvOnly` updates so LTV only moves upward for accounts with debt (downgrades apply only to debt-free accounts, mirroring `favors_liquidator`/`debt_free` logic), or enforce a post-restamp check that the account's LTV-weighted collateral still covers its debt before committing `set_supply_positions` (`params.rs:218`).

### Proof of Concept
1. Alice supplies USDC and borrows; her `AccountPosition.loan_to_value` is cached at the then-listed 80%.
2. Governance reduces USDC's listed LTV to 50%. Alice's stored 80% snapshot remains.
3. Attacker calls `controller.update_account_threshold(attacker, false, [alice_account_id])` — only `attacker.require_auth()` is needed.
4. `sync_account_thresholds` → `refresh_supply_risk_params` unconditionally writes `position.loan_to_value = 50%` for each of Alice's listed supply assets and persists them.
5. Alice calls `withdraw(alice, id, [(USDC, amt)], ...)`; the post-pool LTV-weighted coverage check now uses 50% and reverts, freezing her collateral until she repays debt or LTV is raised.