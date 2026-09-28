### Title
Unbounded chunked-accrual loop in `global_sync` permanently DoSes a dormant market - ([File: contracts/pool/src/interest.rs])

### Summary
Every state-changing pool operation first runs `global_sync`, which compounds indexes in a `while` loop whose iteration count is `elapsed_ms / MAX_COMPOUND_DELTA_MS` — a value that grows with wall-clock time since the market's last touch, not with anything the caller controls. A market left untouched long enough requires more loop iterations than fit in a Soroban transaction budget, and since the loop is all-or-nothing and the gap only widens with time, every subsequent operation on that market reverts forever.

### Finding Description
In `contracts/pool/src/interest.rs`, `global_sync` computes `remaining = cache.elapsed_ms()` and loops `while let Some(nonzero) = NonZeroU64::new(remaining)`, consuming at most `MAX_COMPOUND_DELTA_MS` per iteration with no upper bound on iteration count and no way to accrue partially [1](#0-0) . `global_sync` is invoked at the top of pool market operations via `contracts/pool/src/ops/mod.rs` / `ops/market.rs`, so `supply`, `withdraw`, `borrow`, `repay`, `seize`, `flash_loan`, and `claim_revenue` all pay the full catch-up cost in a single transaction.

This mirrors the reported bug class exactly: the heaviest loop's bound is set by previously accumulated state (elapsed time ↔ processed burn requests), the work per iteration is non-trivial (RAY fixed-point `accrue_step`), there is no mechanism to process a subset (no "un-process" and no partial accrue), and all other flows on the market are gated behind the completing call. Unlike the EVM report where iteration count depends on operator-processed requests, here any unprivileged user can simply let a low-activity market go dormant — or deliberately create a market, touch it once, and wait. Each accrual chunk is pure computation, so the cost is deterministic and grows linearly with dormancy.

### Impact Explanation
Permanent freezing of funds for that market. Suppliers cannot withdraw, borrowers cannot repay or be liquidated, and revenue cannot be claimed, because every path runs `global_sync` first and the transaction exceeds budget. The freeze is self-reinforcing: time only increases `elapsed_ms`, so once the required iteration count exceeds the per-transaction CPU limit, no transaction can ever catch up. The project's own docs acknowledge the exposure: "Position/route limits reduce work but do not prove every maximum-size operation fits deployed CPU, memory, footprint, and oracle-call budgets" and the Certora suite explicitly leaves "unbounded multi-year accrual" outside the proof model [2](#0-1) .

### Likelihood Explanation
Low-to-moderate. It requires a market to remain untouched for a long contiguous period — plausible for a newly listed, illiquid, or deprecated spoke asset with no active borrowers — but the threshold gap is large (many chunks × `MAX_COMPOUND_DELTA_MS`), and any single keeper touch resets the timer. A determined attacker cannot accelerate it, only exploit neglect; however, once triggered it is irreversible, and `simulate_update_indexes`/`update_indexes` provide no chunked-commit escape hatch since accrual is atomic.

### Recommendation
Cap the accrual gap: either clamp `remaining` to a maximum catch-up window per call and allow the accrual to be resumable (persist a partially advanced `last_timestamp`), or bound `elapsed_ms` by treating accrual older than a cutoff as a single terminal chunk (rates saturate anyway at `max_borrow_rate`). A resumable accrual lets any user unstick the market with multiple bounded transactions, analogous to bounding burn requests per epoch in the original report.

### Proof of Concept
1. Admin lists a hub asset; a user supplies a small amount so the market has nonzero `supplied` and `last_timestamp` is set.
2. No one touches the market for `N × MAX_COMPOUND_DELTA_MS` milliseconds where `N` is the number of `accrue_chunk` iterations that exceeds the Soroban per-transaction CPU budget.
3. Any call — `supply`, `withdraw`, `repay`, `liquidate`, `update_indexes`, `claim_revenue` — enters `global_sync`, runs `N` iterations of `accrue_step` in one transaction, and traps on budget.
4. Because `elapsed_ms` is monotonically increasing and there is no partial-accrue path, every retry fails identically; all funds in that market are frozen permanently.

### Citations

**File:** contracts/pool/src/interest.rs (L20-33)
```rust
pub(crate) fn global_sync(env: &Env, cache: &mut Cache) {
    if !cache.needs_accrual() {
        return;
    }

    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
    }

    cache.mark_accrued();
}
```

**File:** docs/explanation/threat-model.md (L326-331)
```markdown
Position/route limits reduce work but do not prove every maximum-size operation
fits deployed CPU, memory, footprint, and oracle-call budgets. Caller-supplied
vectors still cost resources. A full-risk threshold refresh aborts the entire
batch if an included account's final health factor is below 1.05. Isolate and
investigate that account; no earlier updates from the failed batch persist.
An LTV-only refresh has no such final gate.
```
