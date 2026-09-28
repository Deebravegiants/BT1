## Verdict: No analog

The txgbe bug is a round-up-past-the-caller-buffer class: `round_up(length, 4)` bytes are written into a buffer sized for `length`, so the last partial dword overflows the destination. The analogous contract-level shape would be code that computes a rounded-up quantity and applies it without clamping to the caller's intended bound — e.g., crediting/burning/paying a ceiling-rounded amount that exceeds the input, with the excess landing somewhere it shouldn't.

That shape does not exist in the reachable paths:

- **`resolve_repay`** (`contracts/pool/src/cache/scale.rs:111`, `common::rates::resolve_repay`) ceiling-rounds the full-close debt, but returns the overpayment explicitly and the pool refunds it — the excess is clamped, not written past the bound.
- **`resolve_withdrawal`** (`scale.rs:97`) caps burned shares at `pos_scaled`, so a rounded amount cannot exceed the position.
- **`apply_bad_debt_to_supply_index`** (`contracts/pool/src/interest.rs:73-89`) caps the ceil-rounded write-off at `total_supplied_value` and floors the resulting index at `SUPPLY_INDEX_FLOOR_RAW`, so the socialized loss cannot exceed the buffer (supply claims) it writes into.
- **Liquidation repayment legs** are capped per-leg at ceiling-rounded debt, with excess listed as a refund and either never pulled (partial plan) or pulled and refunded by the pool (full-debt plan) — documented in `docs/reference/invariants.md` INV-LIQ-02 and `docs/reference/formulas.md`.
- **Whole-unit seizure** (`contracts/controller/src/positions/liquidation/math.rs:235`) raises a sub-3-decimal quote to one unit, but the unseized margin is explicitly refunded; nothing is written beyond the backed amount.
- **Chunked accrual** (`interest.rs:20-33`) splits elapsed time into `min(remaining, MAX_COMPOUND_DELTA_MS)` chunks and decrements `remaining` by the exact chunk — the final partial interval is applied, not rounded up.

Every place the code rounds up a quantity, the excess over the caller's bound is either clamped (`min`, cap at position/supply value) or returned as a refund. There is no "copy `round_up(n)` into a size-`n` destination" pattern in the in-scope production code, so no valid analog exists.