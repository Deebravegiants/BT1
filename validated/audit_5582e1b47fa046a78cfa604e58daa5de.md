### Permissionless accrual cadence can suppress protocol fee shares - (File: contracts/pool/src/interest.rs)

### Summary

The pool’s permissionless `update_indexes` / market synchronization lets any caller choose how a period of interest is partitioned into accrual steps. Each step calculates and mints protocol revenue shares immediately, including floor-rounding share conversion, instead of accumulating the reserve-factor amount over the full elapsed window and settling it once. Consequently, an unprivileged caller can force frequent accruals and shift value away from suppliers or leave protocol reward value unrepresented by minted revenue shares. This is analogous to the cited checkpoint-boundary flaw: the security result depends on when the window is sampled, and a party can place transactions immediately after a boundary to control the next calculation.

### Finding Description

`contracts/pool/src/ops/mod.rs::synced_market` loads a market and calls `interest::global_sync` before every mutation. `global_sync` chunks only intervals larger than `MAX_COMPOUND_DELTA_MS`; otherwise, the caller-selected interval is accrual as a whole and `mark_accrued` stamps it as complete. The step calculation in `common::rates::accrue_step` recomputes utilization and converts the current protocol reward to shares during that step.

The repository’s own cadence analysis identifies the exploitable shape: `contracts/pool/tests/interest.rs` states that “frequent accrual floors the protocol fee to zero before the reserve factor applies” and that `update_indexes` is permissionless, so the attacker chooses the cadence. The fuzz target likewise states that no partition may strand value, but records two real cross-path effects: early fee shares compound, shifting value from suppliers to the treasury, and frequent utilization re-evaluation can charge borrowers less interest than a single terminal accrual.

The issue is therefore not merely that views are stale. A caller can make a boundary occur at the current ledger by calling `update_indexes` or by submitting any market mutation that invokes `synced_market`. Once `last_timestamp` is stamped, subsequent same-ledger mutations see `elapsed_ms() == 0`; later mutations accrue from the new state chosen by the attacker rather than continuously carrying the previous utilization/rate history.

### Impact Explanation

The economic impact depends on market size, elapsed time, rate model, and call cadence. In the intended case, one terminal accrual allocates the period’s interest between suppliers and the protocol under one utilization/rate calculation. With attacker-selected accrual boundaries, the same nominal elapsed span can allocate a different amount: protocol fee shares minted early join `supplied` and affect later chunks, while later chunks use newly committed utilization. Tests characterize the result as a shift from suppliers to the treasury and the possibility that partitioned accrual charges borrowers less interest than a single accrual.

This can cause loss of unclaimed yield rather than direct seizure of principal. Because `update_indexes` is permissionless and every controller pool mutation also synchronizes first, the path is reachable by an unprivileged address. The impact can become material when a large book accrues over a long interval and an attacker or ordinary activity forces unfavorable partitioning.

### Likelihood Explanation

The trigger is simple: submit `update_indexes` or another market operation at selected ledger times. The attacker does not need governance permissions, leaked keys, oracle dishonesty, or a privileged role.

However, the attacker cannot freely set ledger timestamps; they can only choose when to invoke accrual. Profitability also depends on whether they can benefit from the changed allocation, for example through protocol revenue ownership, supplier positions, or reduced borrowing cost after manipulating utilization. The code and tests establish that cadence changes outcomes, but the repository does not provide a concrete net-profitable theft amount for a particular deployed market. That limits confidence in a high-severity rating without market-specific parameters.

### Recommendation

Make accrual economically cadence-resistant rather than treating each permissionless call as an independent checkpoint:

- Accumulate protocol rewards as an unconverted value within an accounting period and mint revenue shares at a coarser, governance-defined interval.
- Carry pending fee value through intermediate accrual steps so each step’s rounding cannot destroy or reclassify the fee.
- Alternatively, calculate allocation deterministically for the full elapsed period first, then apply any bounded compounding chunks only to index evolution, not to fee-share conversion.
- Add regression tests comparing one terminal accrual with attacker-selected partitions and assert that supplier rewards, borrower charges, and protocol revenue differ only by an explicit, bounded rounding allowance.

### Proof of Concept

The repository already contains the relevant executable model:

1. Seed a supplied and borrowed market with positive utilization and nonzero reserve factor.
2. Record the borrower interest, supplier rewards, and revenue shares produced by one accrual over `total_ms`.
3. Call permissionless `update_indexes` at several intermediate timestamps over the same `total_ms`.
4. Compare the final committed indexes, supplier value, borrower debt, and revenue shares.

The cadence tests in `contracts/pool/tests/interest.rs` and `tests/fuzz/fuzz_targets/rates_and_index.rs` explicitly model this scenario. They show that caller-chosen partitioning can alter interest charged and the allocation between supplier rewards and treasury revenue, including the case where frequent accrual floors a protocol fee to zero before the reserve factor is applied.