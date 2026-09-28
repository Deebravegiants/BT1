### Title
Unfunded `recapitalize`/`repay` refunds pay out of pool custody without verifying inbound transfer - (File: contracts/pool/src/ops/recapitalize.rs)

### Summary
The kernel bug leaks memory because `sk_msg_alloc()` can partially allocate and the caller skips `sk_msg_trim()` on the error path — resources are consumed without matching ownership. The analog in XOXNO Lending is a resource-accounting mismatch in the pool's refund paths: `ops::recapitalize::apply` and `ops::repay::apply` refund a *declared* excess (`amount - applied` / overpayment) via `cache.transfer_out(payer, ...)` without ever checking that `amount` was actually transferred in. The pool pays real custody against an unfunded claim, draining supplier funds. The repo's own test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` (`contracts/pool/tests/flows.rs:3408`) proves custody reaches zero and subsequent withdraws then fail inside the SAC transfer because the cash book still overstates custody.

### Finding Description
`ops::recapitalize::accounting` credits only `min(amount, backing_shortfall)` to cash, but `apply` then transfers `refund = amount - applied` to `payer` unconditionally. The pool contract "does not pull funds from `payer`" (`contracts/controller/src/external/pool.rs:128-138`) and — unlike `supply`, which is prefunded-and-measured by the controller — performs no balance-delta measurement of the inbound transfer. The exact same shape exists in `ops::repay::apply`: `resolve_repay` turns any amount above `current_debt_ceil` into `overpayment`, the `RepayRoundsToZeroShares` assert passes on its `net_repay == 0` disjunct, and the full overpayment is refunded out of custody with the book untouched (`contracts/pool/tests/flows.rs:3578-3611`).

### Impact Explanation
An unprivileged address calls `recapitalize` (or `repay` against a market where a debt leg can be resolved to zero) with a large `amount` and transfers nothing. The pool's SAC transfer of the "refund" pays out of genuine supplier custody. Result: theft of user funds plus a permanently overstated cash book — suppliers' withdraws pass the `require_reserves`/liquidity guards (which read the book) but revert inside the token transfer, freezing remaining funds.

### Likelihood Explanation
The attack is a single call with attacker-chosen arguments; the tests demonstrate it end-to-end, including that no pool guard fires (the failure later surfaces as raw SAC `BalanceError = 10`, not `InsufficientLiquidity`/`PoolInsolvent`). One residual uncertainty: I could not fully verify whether pool endpoints require controller-only auth; however the pool's own tests invoke `repay`/`recapitalize` directly with a generated `payer` and no `require_auth`, and the codebase documents the pre-funding as a caller convention rather than an enforced check.

### Recommendation
Measure the actual inbound balance delta in `recapitalize`/`repay` (as `refund_controller_balance_delta`/`balance_delta_since` do on the controller side), and size `applied`/`refund` from the measured delta, not the declared `amount`. Alternatively, debit `cash` for the refund and route it through `require_reserves` so an unfunded refund can never exceed real receipts.

### Proof of Concept
See `contracts/pool/tests/flows.rs:3408-3483` (`test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody`) and `:3589-3611` (`test_unfunded_repay_overpayment_refund_also_pays_out_of_custody`): a generated `payer` calls `recapitalize(hub, payer, custody)` with zero tokens sent; `token.balance(pool)` drops to 0 while the cash book still shows the deposit, and the supplier's subsequent `withdraw` fails inside the SAC transfer.