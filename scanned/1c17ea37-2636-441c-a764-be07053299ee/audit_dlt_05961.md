# [?] fix(avm): avoid data race on shared interaction selector writes (#24456)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-07-02
Source: https://github.com/AztecProtocol/aztec-packages/commit/e3f3a1464577b3b4d0371e1ad9fa5203da3becd3
Type: security-commit

## Details
fix(avm): avoid data race on shared interaction selector writes (#24456)

## What was wrong

The interactions tracegen phase runs every lookup/permutation job
concurrently: `AvmTraceGenHelper::fill_trace_interactions` concatenates
all builders' jobs and dispatches them with `parallel_for`. Lookups
whose fine-grained destination selector is a *shared* column
(`DST_SELECTOR != outer_dst_selector`) can resolve to the same `dst_row`
from different jobs, so multiple threads write the same `(selector,
row)` cell at once.

The previous code did a guarded read-modify-write on that shared cell:

```cpp
if (DST_SELECTOR != outer_dst_selector && trace.get(DST_SELECTOR, dst_row) != 1) {
    trace.set(DST_SELECTOR, dst_row, 1);
}
```

Both the `get` and the non-atomic 32-byte `set` race against the other
threads' writes to the same cell — a data race, i.e. undefined behavior.
In practice it produced the right value (every writer stores `1`), but
it is still UB.

## The fix

Add an opt-in `use_atomic_limbs` flag to `TraceContainer::set`. When
set, the field's four 64-bit limbs are written with **relaxed atomic
stores** — four plain `movq` on x86-64, no lock and no libatomic call.
(A whole-field `std::atomic_ref<FF>` is *not* an option on the hot path:
at 32 bytes it exceeds the hardware lock-free width and falls back to a
locked libatomic call.)

The shared selector write now uses it and drops the guard read:

```cpp
if (DST_SELECTOR != outer_dst_selector) {
```

_Trimmed to 38 lines — full report: https://github.com/AztecProtocol/aztec-packages/commit/e3f3a1464577b3b4d0371e1ad9fa5203da3becd3_
