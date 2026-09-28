### Title
Protocol fee shares are minted on accrued-but-uncollected interest and are never clawed back when that interest is socialized as bad debt, so suppliers pay a fee on yield they never receive - (File: contracts/pool/src/interest.rs)

### Summary
`accrue_step` splits each accrual window's *booked* borrow interest into supplier rewards and a protocol fee, and `accrue_chunk` immediately mints the fee as revenue shares (`accrue_revenue` increases both `revenue` and `supplied`). The interest is only a debt-accounting entry at this point — no cash has arrived. When a borrower's position later becomes unrecoverable, `seize::apply` (Borrow side) calls `apply_bad_debt_to_supply_index`, which scales the supply index down pro-rata across *all* supply shares. Nothing removes or compensates the revenue shares that were minted on the now-written-off interest. The protocol keeps a claim on the remaining pool value that was priced off interest that was never paid, diluting every LP's recovery. This is the same bug class as the Astaria report: the protocol fee is charged on a schedule (accrual/minting) that does not match when interest is actually received, so LPs fund a fee on phantom yield.

### Finding Description
The accrual pipeline is:

- `common/src/rates/simulate.rs::accrue_step` computes `accrued_interest` as the *booked* debt growth `borrowed × (borrow_index' − borrow_index)`, splits it by `reserve_factor`, and emits `revenue_shares` valued at the new supply index (`common/src/rates/index.rs::calculate_supplier_rewards`, `protocol_fee_shares`).
- `contracts/pool/src/interest.rs::accrue_chunk` commits the step via `cache.accrue_revenue(step.revenue_shares)`, which does `revenue += s; supplied += s` (`contracts/pool/src/cache/shares.rs:36-39`) — new claims minted against cash that has not been repaid.
- If the underlying debt later defaults, `contracts/pool/src/ops/seize.rs::apply` (Borrow side) runs `apply_bad_debt_to_supply_index`, which reduces `supply_index` by `bad_debt / total_supplied_value` (`contracts/pool/src/interest.rs:73-88`). `total_supplied_value` includes the fee shares minted on the very interest being written off.

Because the write-down is applied as a uniform index reduction, the protocol's minted fee shares retain a proportional claim on post-write-down value. Had the fee never been minted, LPs would own 100% of the remaining pool; instead they cede the treasury's fraction forever. The fee on never-received interest is not reversed at seize time, and `recapitalize` explicitly refills cash without minting or burning shares, so it does not unwind the dilution either.

### Impact Explanation
Permanent loss of LP funds equal to the protocol's revenue-share fraction of the post-write-down pool, attributable to fee minted on interest that was never collected. On a market that accrues a large fee position against a borrower that later defaults (e.g. stale oracle gap, illiquid collateral, dust-threshold cleanup delay), `clean_bad_debt` — callable by any unprivileged address via the controller's `clean_bad_debt`/`liquidate` paths into `pool_seize_positions_call` — finalizes a state where suppliers absorb the full bad debt *and* remain diluted by revenue shares priced off that same phantom interest. This is theft/misallocation of user funds in favor of protocol revenue.

### Likelihood Explanation
Medium. It requires a bad-debt event, which is the pool's designed-for tail case (dust-threshold cleanup, `apply_bad_debt_to_supply_index` floor). No privileged action, timing luck beyond ordinary liquidation delay, or oracle manipulation is needed — any account that goes underwater past the liquidation/cleanup threshold triggers the path, and every prior accrual window has already minted fee shares on its unpaid interest. The loss per event is bounded by `reserve_factor × written-off interest`, matching the original Medium severity.

### Recommendation
On bad-debt socialization, claw back the portion of `revenue` shares that was minted against the uncollected interest being written off (e.g. compute the fee shares attributable to the seized debt's accrued interest and burn them alongside `burn_debt`), or defer fee minting until interest is actually repaid — only call `accrue_revenue` for fees backed by cash flows (repay/liquidation/flash), tracking accrued-but-unpaid fee off-book. Alternatively, when computing `apply_bad_debt_to_supply_index`, net the protocol's revenue claim out of the socialized loss so the treasury absorbs its pro-rata share of the write-down first.

### Proof of Concept
```text
1. Supplier S supplies 1_000 XLM to the (hub, XLM) market; B borrows 800.
2. Time passes; anyone calls pool.update_indexes (or any op that runs
   interest::global_sync). accrue_step books I = interest on B's debt and
   mints reserve_factor × I worth of revenue shares:
   supplied = S_shares + fee_shares; no XLM has been repaid.
3. B's collateral crashes / position is abandoned below the dust threshold.
   A permissionless caller invokes controller.liquidate / clean_bad_debt.
4. seize::apply(Borrow side): bad_debt = B's full debt (incl. I) is socialized —
   supply_index is scaled down by bad_debt / (supplied × supply_index).
   fee_shares minted in step 2 remain outstanding.
5. S withdraws: S now owns S_shares / (S_shares + fee_shares) of the remaining
   pool value. Without the fee mint on the never-paid interest I, S would own
   S_shares / S_shares = 100% of the post-write-down value.
   => S paid the protocol fee on interest it never received.
```

Relevant code: `accrue_step` fee mint (`common/src/rates/simulate.rs:68-87`), `accrue_revenue` (`contracts/pool/src/cache/shares.rs:36-39`), bad-debt socialization without fee clawback (`contracts/pool/src/interest.rs:73-88`, `contracts/pool/src/ops/seize.rs:24-28`).