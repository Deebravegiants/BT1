### Title
Unfunded overpayment refund drains pool cash — `repay`/`recapitalize` refund from a declared amount that was never deposited - (File: contracts/pool/src/ops/repay.rs)

### Summary
The double-free bug class (releasing a resource that was never / no longer owned) maps onto the pool's excess-payment refund path. `ops::repay::accounting` and `ops::recapitalize::accounting` compute a refund purely from the *declared* `amount` and hand real tokens back via `transfer_out`, without debiting `cash`, checking `require_reserves`, or verifying that any tokens were actually received in the same call. When the declared amount exceeds real obligations (e.g., repaying a position with zero debt), the entire amount is treated as "overpayment" and refunded out of pool custody — funds that belong to suppliers.

### Finding Description
In `contracts/pool/src/ops/repay.rs`, `accounting` resolves `action.amount` into burned debt shares plus an `overpayment`, then `apply` executes `outcome.cache.transfer_out(payer, outcome.overpayment)` at line 32. The refund is derived from the declared `PoolAction.amount`, not from a measured inbound balance delta. The cash book is only credited by `net_repay` (`credit_cash(net_repay)`, line 57); the outbound refund is never debited and never passes a reserve check — this is only sound *if* the controller pre-funded the full declared amount in the same transaction (`positions/debt.rs::settle_repay` lines 144–152 use `transfer_amount_measured`).

The repo's own test `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` (`contracts/pool/tests/flows.rs:3590-3611`) demonstrates the failure mode: calling `pool.repay` with a declared amount equal to the pool's entire token balance, against a market with zero debt, makes `resolve_repay` take the full-close branch with `net_repay = 0`, the `RepayRoundsToZeroShares` assert passes on its `net_repay == 0` disjunct (`repay.rs:48-52`), and `assert_unfunded_refund_drained_custody` confirms the full custody balance was transferred out with the book untouched. The same shape exists in `ops::recapitalize::apply` (`recapitalize.rs:34`), where `refund = amount − min(amount, backing_shortfall)` is paid out of custody; with no shortfall, `applied = 0` and the whole declared `amount` is refunded.

The trust boundary is the issue: correctness depends entirely on the caller having transferred `amount` first. If `pool.repay`/`pool.recapitalize` can be invoked directly by an unprivileged address (the test calls `client().repay(&payer, ...)` with a generated payer and no inbound transfer), or via any controller path that forwards a declared rather than measured amount, the "refund" frees tokens the contract never received — the accounting analog of a double free. I could not fully verify the authorization gating in `pool/src/lib.rs` (grep returned no usable content for the auth checks); if repay/recapitalize require the controller as caller, severity drops since all controller paths observed (`settle_repay`) fund via `transfer_amount_measured` first.

### Impact Explanation
Theft of user funds / protocol insolvency. The refund transfers real tokens out of pool custody while `cash`, `supplied`, and `borrowed` are unchanged, so suppliers' claims now exceed actual holdings. A single call with `amount` set to the pool's full token balance and zero outstanding debt withdraws the entire balance (demonstrated in `flows.rs:3610`), leaving the market insolvent and unable to honor withdrawals.

### Likelihood Explanation
High if the pool entrypoints are reachable without the controller's pre-funding: the exploit requires no price manipulation, no collateral, and no existing position — just a `PoolAction` with a large declared amount. The only mitigation found is the convention that "the controller transfers the amount into the pool before this call" (`repay.rs:3`, `recapitalize.rs:4`); nothing in the pool enforces it. Likelihood is low if `lib.rs` restricts these ops to the controller address, which I was unable to confirm within the available context.

### Recommendation
Make the refund self-funding inside the pool: snapshot the pool's token balance at entry and cap `overpayment`/`refund` at the measured inbound delta (`balance_after_start − balance_before`), mirroring the controller's `transfer_amount_measured`/`balance_delta_since` pattern in `contracts/controller/src/payments.rs:10-20`. Alternatively, require the controller as the authenticated caller for `repay`/`recapitalize` and debit the refund from `cash` with a `require_reserves` check so an unfunded refund cannot exceed tracked reserves.

### Proof of Concept
As encoded by the existing test in `contracts/pool/tests/flows.rs:3590-3611`:

1. Attacker calls `pool.repay(payer = attacker, action = PoolAction { position: <zero-debt position>, amount = token.balance(pool), hub_asset })` with no token transfer.
2. `resolve_repay` sees `current_debt_ceil == 0`, takes the full-close branch → `overpayment = amount`, `net_repay = 0`.
3. The assert at `repay.rs:50` passes (`net_repay == 0`).
4. `transfer_out(attacker, overpayment)` moves the pool's entire token balance to the attacker; `cash`, `supplied`, `borrowed` unchanged → insolvent market.

Same shape for `recapitalize`: call with `amount = pool balance` on a market with zero `backing_shortfall` → `applied = 0`, `refund = amount` paid out of custody (`recapitalize.rs:52-55, 34`).