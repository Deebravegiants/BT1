### Title
Whale can saturate `supply_cap` to block collateral top-ups and force liquidations - (File: contracts/controller/src/spoke_usage.rs)

### Summary
Each (spoke, asset) market enforces an asset-unit `supply_cap` on entry. Any unprivileged user can fill the cap with their own supply, causing every subsequent `supply` into that spoke to revert with `SpokeSupplyCapReached`, then withdraw at will since exits never check caps. A borrower whose health factor is deteriorating can be permanently prevented from adding collateral, letting the attacker liquidate them — the same deny-deposit-to-manipulate-market class as the reference `maxContractBalance` report.

### Finding Description
`SpokeUsageContext::apply_entry` calls `enforce_spoke_cap`, which converts the configured cap to RAY-scaled shares and reverts if `usage + new_shares > cap_scaled` (`contracts/controller/src/spoke_usage.rs:144-156`). Cap tracking is per spoke usage row (`SpokeUsageRaw.supplied_scaled_ray`), shared across all users of that spoke. `apply_exit` subtracts usage with no cap check (`spoke_usage.rs:119-139`), so the attacker recovers funds freely. `supply` and `withdraw` are permissionless user entrypoints, so a single address can: (1) supply up to the cap, (2) wait for/transact ahead of a victim's collateral top-up or new supply, which reverts, (3) liquidate the now-undercollateralized victim via `liquidate`, (4) withdraw. Unlike the reference report, the attacker even earns supply interest while occupying the cap, and no front-running is needed — they can simply hold the cap saturated continuously on a thin-cap spoke.

### Impact Explanation
Strategic denial of deposits: victims cannot add collateral to a distressed position, so a position that would have remained healthy is forced into liquidation; the attacker captures the liquidation bonus. For users not yet in the market it is a temporary deposit DoS on that spoke. Because caps are per spoke, the attack is confined to positions collateralized through that spoke — Medium severity.

### Likelihood Explanation
Requires only capital equal to `supply_cap` minus existing usage, which on newly listed or intentionally small-cap markets may be modest, and the capital is neither at risk nor idle (it accrues yield). No privileged access, timing trick, or oracle manipulation needed. It fails only if the victim can migrate to another spoke listing the same collateral or if caps are set at the domain ceiling (`max_cap_for_decimals`), where saturation is economically infeasible.

### Recommendation
Treat the cap as a soft backstop rather than a hard ceiling for defensive actions — e.g., exempt supply that increases collateral on an account with HF < 1, or enforce caps only above a utilization threshold. At minimum, document that supply caps create a griefing surface and size them high enough that saturating one is uneconomical, or make cap-fill block only new accounts rather than top-ups to existing accounts (track per-account share of usage is not feasible with aggregate usage, so raising the cap or HF-based exemption is the practical fix).

### Proof of Concept
1. Admin lists asset X in spoke S with `supply_cap = C` via `EditAssetInSpoke`; existing usage is `U < C`.
2. Victim supplies X as collateral in spoke S and borrows; price drift pushes HF toward 1.
3. Attacker calls `supply` on spoke S with `C − U` of X — `enforce_spoke_cap` passes, `supplied_scaled_ray` now equals `cap_scaled`.
4. Victim's `supply` of additional X reverts with `SpokeSupplyCapReached` (#311) since `usage + delta > cap_scaled` (`spoke_usage.rs:155`); every retry fails while the attacker holds.
5. HF crosses 1; attacker calls `liquidate` and seizes collateral with the bonus.
6. Attacker calls `withdraw` — `apply_exit` subtracts usage with no cap check — recovering principal plus interest.

Test `test_spoke_spoke_supply_cap_headroom_restored_after_withdraw` (`tests/test-harness/tests/controller/spoke.rs:968-993`) demonstrates exactly this mechanic: supply fills the cap, further supply reverts, withdraw restores headroom — the attack is steps 3–6 with a victim's liquidation inserted between.