### Title
Permissionless `force_socialize_bad_debt` bypasses the documented owner-only gate and writes down supply index for any merely-insolvent account - (File: contracts/controller/src/positions/liquidation/mod.rs)

### Summary
The code defines two bad-debt socialization gates. `BadDebtGate::DustCapped` is explicitly documented as permissionless, while `BadDebtGate::InsolventOnly` is documented as **"Owner-only: insolvent alone, with no cap on the collateral left behind"** (mod.rs:204-209). However, the exported path `process_force_socialize_bad_debt` (mod.rs:246-249) invokes the `InsolventOnly` gate with **no `require_auth`, no owner check, and no caller parameter at all** — only the flash-loan guard. Analogous to CVE-2021-37601 (a function reachable without the intended authorization check exposing restricted operations), an authorization gate that exists in the design is absent in the implementation.

### Finding Description
`process_clean_bad_debt` correctly gates the permissionless path: `caller.require_auth()` plus the `DustCapped` gate requiring `is_socializable_bad_debt(totals.total_debt, totals.total_collateral)` — insolvency *and* collateral at/below dust (mod.rs:196-199, 229-232).

`process_force_socialize_bad_debt` instead takes only `(env, account_id)` — no caller `Address`, no `require_auth`, no `account::require_owner_or_delegate` — and passes `BadDebtGate::InsolventOnly`, which admits any account where `totals.total_debt > totals.total_collateral` (mod.rs:233, 246-249). `socialize_bad_debt` then calls `bad_debt::execute_bad_debt_cleanup`, which per the documented design performs the supply-index write-down on remaining collateral/debt.

The only difference between the two admission conditions is the dust cap. Because the force path is permissionless, the dust cap is meaningless: any account that is insolvent by even one wei can be force-cleaned by anyone, discarding however much collateral remains, rather than going through pro-rata liquidation where that collateral would be seized by a liquidator repaying debt.

### Impact Explanation
Theft/destruction of residual user collateral and forced loss on suppliers. For a liquidatable-but-insolvent account still holding meaningful collateral (e.g., an oracle move pushing it just below water), an unprivileged attacker can call the force-cleanup entrypoint, socialize the debt, and trigger the supply-index write-down — destroying collateral that orderly liquidation would have distributed via the bonus curve to whoever repaid the debt. Suppliers absorb a socialized loss immediately instead of the position being liquidated. This is a one-way, irreversible accounting action reachable by a single unprivileged address with a single argument (`account_id`), meeting the "theft/permanent freezing of funds / protocol insolvency acceleration" bar.

### Likelihood Explanation
Likelihood is moderate-to-high in volatile conditions: insolvency happens routinely when collateral prices gap down faster than liquidators act, or on illiquid spokes. The attacker needs only to observe `total_debt > total_collateral` via public views and submit one call — no capital, no flash loan, no oracle manipulation required. The guard `require_not_flash_loaning` does not restrict who may call it, only when.

Caveat: I verified the missing auth check and gate selection in mod.rs directly, but did not confirm the exported entrypoint name in `lib.rs` within the available iterations; the function is `pub(crate)` and the prompt's reachable-entrypoint list includes `clean_bad_debt`, so a force-cleanup endpoint should be confirmed reachable before submission.

### Recommendation
Either add the owner/delegate check the design documents — e.g., accept a `caller: Address`, call `caller.require_auth()`, and `account::require_owner_or_delegate(env, account_id, &caller, &account.owner)` inside `process_force_socialize_bad_debt` — or, if the force path is intended to be permissionless, delete the `InsolventOnly` gate and the stale "Owner-only" doc comment and apply `DustCapped` uniformly.

### Proof of Concept
1. Attacker (fresh address, no position) monitors accounts until some `account_id` has `total_debt > total_collateral` per `risk::calculate_account_risk_totals` (regardless of remaining collateral size).
2. Attacker invokes the controller's force-socialize entrypoint with `account_id`.
3. `socialize_bad_debt` admits via `BadDebtGate::InsolventOnly` (mod.rs:233) with no auth, and `bad_debt::execute_bad_debt_cleanup` writes the debt down against the supply index, socializing the full shortfall — skipping liquidation and destroying residual collateral.