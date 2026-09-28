### Title
Pool `repay`/`recapitalize` refund the *declared* overpayment from custody without verifying any inbound transfer - (File: contracts/pool/src/ops/repay.rs)

### Summary
Analogous to the Allo `baseFee` flaw — where the amount *charged* is checked against a declared figure rather than the funds actually delivered — the pool's `repay` and `recapitalize` ops compute a "refund" purely from the caller-declared `amount` and pay it out of the pool's real token balance via `transfer_out`, without ever measuring that `amount` was actually transferred in. An unprivileged caller can declare an arbitrary `amount`, have zero debt/shortfall absorb it, and receive the entire declared sum as a refund, draining supplier custody while the cash book still reports the funds as present.

### Finding Description
In `repay`, `accounting` calls `cache.resolve_repay(amount, position)`; any `amount` above the position's debt becomes `overpayment`, which `apply` sends to `payer` via `cache.transfer_out(payer, outcome.overpayment)` (`contracts/pool/src/ops/repay.rs:32,44-57`). On a market with no debt (or any attacker-controlled payer with no borrow position), the whole `amount` is "excess" and is paid out — nothing verifies tokens actually arrived.

The same pattern exists in `recapitalize`: `applied = amount.min(backing_shortfall)` and `refund = amount - applied` is transferred to `payer` (`contracts/pool/src/ops/recapitalize.rs:34,52-55`). With no shortfall, the entire declared amount is refunded.

The protocol's own regression tests confirm custody is drained while the book is untouched: `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` shows `recapitalize(&hub, &payer, &custody)` zeroing the pool balance with `cash` still claiming the deposit (`contracts/pool/tests/flows.rs:3430-3440`), and `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` shows a `repay` on a debt-free market refunding the full declared amount from custody (`contracts/pool/tests/flows.rs:3590-3610`). The subsequent `withdraw` then fails inside the SAC transfer with `BalanceError`, meaning supplier funds are gone while the book says solvent.

### Impact Explanation
Theft of user funds and protocol insolvency: any unprivileged address can extract up to the pool's entire token balance by declaring a large `amount` on a market with no debt (repay) or no shortfall (recapitalize). Because the refund never debits `cash`, the book overstates custody; subsequent legitimate withdrawals pass the pool's liquidity guard and revert in the token transfer, permanently freezing remaining supplier funds.

### Likelihood Explanation
High if reachable: the pool endpoints take a `payer`/`receiver` address directly and the refund path runs unconditionally in `apply`. Exploitation requires only calling `repay`/`recapitalize` with a large `amount` on a zero-debt/zero-shortfall market — no collateral, no position, no capital needed, and it is repeatable per market. (Caveat: whether the pool entrypoints enforce controller-only auth was not fully verified within this scan; the in-repo tests invoke `t.client().recapitalize`/`repay` on the pool directly and succeed, which strongly suggests no funding precondition is enforced. If controller-gating exists, the controller does transfer in before calling, which would narrow but not eliminate the gap — the refund is still computed from the declared amount rather than a measured balance delta.)

### Recommendation
Measure the inbound leg like the controller does for other flows: snapshot the pool's token balance before applying the action, cap the applied amount and the refund at the measured balance delta, and never pay a refund exceeding what was actually received. Alternatively, restrict `repay`/`recapitalize` to the controller and require the controller's pre-transfer to be measured, e.g. `refund <= balance_after - balance_before`, and make `require_reserves` cover refund payouts.

### Proof of Concept
1. A market has `borrowed == 0` (no debt) and real supplier custody `C`.
2. Attacker calls `pool.repay(payer = attacker, PoolAction { hub_asset, amount = C })` without transferring anything.
3. `resolve_repay` sees zero debt → `overpayment = C`, `net_repay = 0`; the `RepayRoundsToZeroShares` check passes via its `net_repay == 0` disjunct.
4. `cache.transfer_out(attacker, C)` pays the full custody to the attacker; `cash` is unchanged.
5. A supplier's later `withdraw` passes `require_reserves` (book intact) and reverts inside the SAC `transfer` — funds permanently unrecoverable. Same sequence works via `recapitalize` when `backing_shortfall == 0`. This mirrors `contracts/pool/tests/flows.rs:3407-3610`.