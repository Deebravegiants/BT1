### Title
Full revenue claim burns the last supply shares while debt is outstanding, permanently DoS-ing `claim_revenue` via `PoolInsolvent` — (File: contracts/pool/src/ops/revenue.rs)

### Summary
The pool's revenue-claim path burns claimable revenue shares out of `supplied` *before* enforcing `require_supply_for_debt`, the invariant that `supplied == 0` implies `borrowed == 0`. Analogous to the quic-go bug — where a premature `HANDSHAKE_DONE` dropped handshake keys while undecryptable packets were still queued, tripping a "nothing left" assertion — a revenue claim that takes `supplied` to zero while `borrowed > 0` unconditionally panics with `CollateralError::PoolInsolvent`. Because the burn amount is not caller-controlled (it is always `min(cash, floor(revenue_value))`), there is no smaller claim that succeeds: the last tranche of protocol revenue in such a market is permanently unclaimable.

### Finding Description
In `contracts/pool/src/ops/revenue.rs:39-48`, `accounting` runs `cache.burn_claimable_revenue()`, then `guards::require_utilization_below_max`, then `guards::require_supply_for_debt`. `burn_claimable_revenue` (`contracts/pool/src/cache/shares.rs:54-75`) pays `min(cash, floor(revenue * supply_index))` and subtracts the burned shares from **both** `revenue` and `supplied`. `require_supply_for_debt` (`contracts/pool/src/guards.rs:69-73`) panics with `PoolInsolvent` when `supplied == 0 && borrowed != 0`.

The reachable bad state is a market where `supplied == revenue` (every user supplier has exited, leaving only protocol revenue shares) while `borrowed > 0` and `cash >= floor(revenue_value)` (low utilization). This state is reachable through ordinary unprivileged flows:

- User withdrawals are gated by `require_supply_for_debt` *after* the burn, but since revenue shares remain inside `supplied`, a full exit of all user supply leaves `supplied = revenue > 0` and is permitted.
- Bad-debt cleanup can also push `revenue` toward `supplied` via `absorb_supply_as_revenue`, and the `SUPPLY_INDEX_FLOOR_RAW` write-down can leave debt claims without supplier backing (documented residual-shortfall case).

Once in that state, `claim_revenue` always computes `amount = min(cash, treasury_actual) = treasury_actual` (cash covers the full claim), so `scaled_to_burn = self.revenue` — the **entire** revenue balance. Burning it drives `supplied` to exactly 0, and `require_supply_for_debt` reverts the whole transaction. The caller cannot request a partial payout to leave one share behind; the entrypoint offers no amount parameter. Every subsequent claim retries the same full burn and reverts identically.

### Impact Explanation
Permanent freezing of unclaimed yield: protocol revenue accrued in the market can never be claimed once the market converges to `supplied == revenue` with outstanding debt and sufficient cash. The freeze is permanent, not temporary — accrual only grows `revenue` (and hence the full burn), and no parameter lets a caller burn less than the computed amount. `recapitalize` cannot repair it either: it fills a cash shortfall, but the blocking condition is zero supply shares, not a backing shortfall.

### Likelihood Explanation
Likelihood is moderate and fully permissionless to trigger the bad state, though the state itself requires all non-revenue supply to exit a market that still has open debt. That is plausible for deprecating/delisted markets, thin markets where a single supplier funded all loans, or markets post-bad-debt cleanup where residual revenue shares dominate `supplied`. `claim_revenue` is callable by any address on the controller, so once the precondition exists the revert is deterministic. Severity: Medium — yield freezing only, bounded by the market's accrued revenue; no user-principal theft or insolvency.

### Recommendation
Apply the guard ordering fix the same way quic-go did (drop Initial keys alongside Handshake keys rather than asserting the queue is empty): cap the burn at `supplied - 1` (or `supplied` minus a minimum residual share) when `borrowed > 0`, i.e. compute `scaled_to_burn = min(scaled_to_burn, supplied.saturating_sub(1))` whenever `borrowed != 0`, leaving the smallest possible supply share so `require_supply_for_debt` is never violated by the claim itself. Alternatively, reorder so the guard clamps the claim (`amount` limited to what keeps `supplied > 0`) instead of reverting after the burn.

### Proof of Concept
1. Governance lists market M; Alice supplies S units, Bob borrows B < S (debt outstanding).
2. Time passes; interest accrues `revenue` shares inside `supplied`. Alice fully withdraws — permitted because post-burn `supplied = revenue > 0`. Now `supplied == revenue`, `borrowed == B > 0`.
3. Keep utilization low enough that `cash >= floor(revenue * supply_index)` (e.g., B small relative to cash, or Bob partially repays without closing).
4. Anyone calls controller `claim_revenue` → `ops::revenue::accounting` → `burn_claimable_revenue` computes `amount = treasury_actual`, `scaled_to_burn = revenue = supplied` → `supplied` becomes 0 → `require_supply_for_debt` panics with `PoolInsolvent`.
5. Repeat forever: the burn amount is deterministic and maximal, so every claim reverts; the revenue is permanently unclaimable.

Caveat: I could not fully trace every path that can produce `supplied == revenue` (e.g., whether post-cleanup states guarantee residual user shares), so the reachability of the exact precondition rests on the withdrawal-absorbing-revenue analysis above; the panic-on-full-burn mechanics are confirmed by `shares.rs:54-75` and `guards.rs:69-73`.