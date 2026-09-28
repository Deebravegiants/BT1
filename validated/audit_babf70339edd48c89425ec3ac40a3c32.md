### Title
Permanent market freeze from RAY-value overflow during mandatory interest accrual - ([File: `common/src/rates/simulate.rs`])

### Summary
Every pool mutation first runs interest accrual. Accrual computes total debt and supply as `scaled_shares * index` in `i128`. Once that product exceeds `i128::MAX`, accrual panics with `MathOverflow` before any requested operation runs, permanently blocking repayment, withdrawal, liquidation, and recapitalization for the market.

### Finding Description
`contracts/pool/src/interest.rs::global_sync` calls `accrue_chunk` for every elapsed accrual window. `accrue_chunk` delegates to `common/src/rates/simulate.rs::accrue_step`, which evaluates `scaled_to_original` for both `borrowed` and `supplied`. `scaled_to_original` in `common/src/rates/scaling.rs` performs checked `Ray` multiplication, so a value above the `i128` range aborts the transaction.

The borrow index is capped at `MAX_BORROW_INDEX_RAY`, but that cap is applied to the index itself, not to the precomputed `borrowed * borrow_index` and `supplied * supply_index` products used during the same accrual step. Consequently, a sufficiently large market can reach the numeric ceiling while the index is still far below its configured cap.

The reachable path is:

1. A user calls `controller.supply` to create collateral in another listed market.
2. The same user calls `controller.borrow` and takes a large position in the target market.
3. Other users may also have supplied the market normally.
4. As time passes at high utilization, any call to `controller.update_indexes` or any operation touching the market runs `global_sync`.
5. Once `borrowed * borrow_index` or `supplied * supply_index` exceeds `i128::MAX`, the accrual aborts.
6. Every later `repay`, `withdraw`, `borrow`, `liquidate`, `flash_loan`, `claim_revenue`, `recapitalize`, and `update_indexes` touching that market aborts at the same first accrual step.

The repository's own regression test `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs::a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates this sequence with a billion-unit 18-decimal market at 98% utilization and confirms that repayment and withdrawal both fail with `MathOverflow`.

### Impact Explanation
All funds in the affected market become permanently inaccessible through the protocol. Suppliers cannot withdraw, borrowers cannot repay or be liquidated, keepers cannot update indexes, and recapitalization cannot execute because every path accrues first. Since pool state cannot be edited by an unprivileged recovery path, the market requires a contract upgrade to recover.

### Likelihood Explanation
The trigger requires a very large market whose RAY-denominated accrued value approaches `i128::MAX`, together with enough elapsed time and utilization for index growth. Whether that is reachable in a particular deployment depends on the configured supply/borrow caps and actual token supply. No privileged action is needed once such a market exists: ordinary `supply`, `borrow`, and permissionless `update_indexes` calls establish the state.

### Recommendation
Make accrual overflow-safe before either index or total-value multiplication exceeds the domain. In particular:

- Bound `borrowed`, `supplied`, and expected index growth so every stored market value remains representable.
- Detect the impending value overflow before `scaled_to_original`, clamp indexes safely, and commit a recoverable terminal state.
- Alternatively use saturating/widening arithmetic for total-value calculations and preserve an emergency repayment or withdrawal path that does not panic during accrual.
- Add an explicit protocol guard before caps or accumulated balances can approach the RAY-value ceiling.

### Proof of Concept
The repository test reproduces the failure:

```rust
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);

// Advance time until accrual overflows.
t.advance_time(YEAR_SECS);
assert_contract_error(
    t.try_update_indexes_for(&["BIG18"]),
    errors::MATH_OVERFLOW,
);

// Both exit and repayment hit the same mandatory accrual panic.
assert_contract_error(
    t.try_withdraw_raw(BOB, "BIG18", 1),
    errors::MATH_OVERFLOW,
);
assert_contract_error(
    t.try_repay(ALICE, "BIG18", 1.0),
    errors::MATH_OVERFLOW,
);
```