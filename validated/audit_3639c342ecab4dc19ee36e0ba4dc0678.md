### Title
`Pool::recapitalize` refunds tokens the payer never deposited — arbitrary drain of pool custody — (File: contracts/pool/src/ops/recapitalize.rs)

### Summary
`recapitalize` documents that "The controller transfers `amount` into the pool before this call" and refunds `amount − backing_shortfall` to the `payer`. The pool never verifies that any transfer actually occurred; it pays the refund unconditionally via `cache.transfer_out(&payer, refund)`. Any unprivileged address can call the pool's `recapitalize` entrypoint directly with `payer = attacker` and an arbitrary `amount`, funding nothing, and receive a refund equal to `amount − backing_shortfall` drawn from the pool's real token custody. This is the exact analog of the M-03 class: the implementation omits a documented precondition (actual deposit of funds), producing a function that pays out value it never received.

### Finding Description
In `contracts/pool/src/ops/recapitalize.rs`:

- `accounting()` computes `applied = amount.min(backing_shortfall(&cache))` and `refund = amount - applied`, credits `applied` to `cash`, and commits — all without reading the pool's token balance or comparing it to a pre-call balance (lines 44–67).
- `apply()` then executes `outcome.cache.transfer_out(&payer, outcome.refund)` (line 34), sending real tokens to `payer`.
- The doc comment states the assumption: "The controller transfers `amount` into the pool before this call" (line 4) — but nothing in the pool enforces it.

The controller-side wrapper `recapitalize()` in `contracts/controller/src/markets.rs:142-164` does prefund the pool via `transfer_amount_measured` before `pool_recapitalize_call`, so the documented flow is safe. The pool entrypoint, however, is directly callable. The protocol's own test suite confirms the exploit shape: `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` (`contracts/pool/tests/flows.rs:3408-3483`) calls `client().recapitalize(&hub, &payer, &custody)` with no prefund, drains the pool's entire token balance to `payer`, and leaves `cash` overstating custody so subsequent withdrawals pass the liquidity guards and fail inside the SAC transfer.

For a healthy market (`backing_shortfall == 0`), `applied = 0` and `refund = amount`, so the attacker's entire requested `amount` (up to pool custody / token balance limits) is paid out as pure profit.

### Impact Explanation
Theft of user funds and protocol insolvency. An attacker can drain the pool's physical token custody in one call by requesting `amount` equal to the pool's token balance. Even after the drain, the `cash` book still records the stolen funds as present, so `require_reserves`/`require_liquidation_buffer` admit withdrawals and borrows that then fail inside the token transfer — the market reports itself solvent while it cannot pay, freezing legitimate suppliers' exits and breaking liquidations. In an under-backed market the attacker still extracts `amount − shortfall` for free.

### Likelihood Explanation
High. The path requires a single unprivileged call to `pool.recapitalize(hub_asset, payer, amount)` with attacker-controlled `payer` and `amount`; `require_auth` on `payer` (if present) is satisfied by the attacker themselves. No prefunding, privileged role, timing window, or price manipulation is needed. The only cost is gas; the payoff is bounded only by pool custody and token transfer limits.

### Recommendation
Measure the pool's actual receipt instead of trusting the caller: snapshot `token.balance(pool)` before the refund, or require the caller to prove custody. Concretely, either (a) restrict `recapitalize` to the controller via `require_auth` on a stored controller address so the only entry is the prefunding wrapper in `markets.rs:142`, or (b) make `accounting` compute `applied`/`refund` against the measured balance delta of the current invocation rather than the declared `amount`. Also consider the defensive fix of paying the refund only after verifying `balance >= cash` post-credit.

### Proof of Concept
```text
// Pool market for (hub_id, USDC) holds 10_000 USDC custody; market is healthy
// (backing_shortfall == 0). Attacker owns no position and deposits nothing.

pool.recapitalize(
    HubAssetKey { hub_id, asset: USDC },
    payer = attacker,          // attacker authorizes their own refund
    amount = 10_000_000_000,   // = pool token balance
);

// accounting: applied = min(amount, 0) = 0; refund = amount - 0 = amount
// apply: transfer_out(attacker, 10_000_000_000) -> drains pool custody
// post-state: token.balance(pool) = 0, cash book unchanged (overstates custody)
```

This mirrors `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` at `contracts/pool/tests/flows.rs:3408-3483`, which demonstrates custody fully drained by an unfunded recapitalize and a subsequent supplier withdrawal failing inside the SAC transfer.