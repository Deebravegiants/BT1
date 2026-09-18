### Title
Unwrap-triggered panic on pnl underflow in `process_withdraw` can permanently deny LP withdrawals - ([File: program/src/processor.rs])

### Summary
The CVE describes a kernel panic (`BUG_ON`) that fires on a legitimate, reachable error condition instead of returning the error gracefully. `Processor::process_withdraw` in `program/src/processor.rs` contains an analogous pattern: after computing `coin_amount`/`pc_amount` via `InvariantPool::exchange_pool_to_token` (floor rounding) it recomputes `target_orders.calc_pnl_x`/`calc_pnl_y` using `checked_sub(...).unwrap()` chains, which will panic instead of returning `AmmError` if the subtraction underflows.

### Finding Description
In `process_withdraw`, `x1`/`y1` are the normalized total pc/coin (after `calc_take_pnl` has already deducted `delta_x`/`delta_y` from the running totals), and `coin_amount`/`pc_amount` are derived independently through a separate, floor-rounded LP-ratio calculation (`InvariantPool::exchange_pool_to_token`). The code then does: [1](#0-0) 
Both `checked_sub` calls are immediately `.unwrap()`ed rather than propagated with `?`, unlike almost every other fallible calculation in the same function (e.g. the `ok_or(...)?` pattern used just above for `coin_amount`/`pc_amount`): [2](#0-1) 
Because `x1`/`y1` and `coin_amount`/`pc_amount` come from two different rounding paths (exact multiplicative normalization vs. floor-divided LP-ratio exchange) plus an additional `delta_x`/`delta_y` subtraction from `calc_take_pnl`, there is no explicit invariant in the code guaranteeing `x1 - normalize(pc_amount) - delta_x >= 0` (and the analogous coin case) for every reachable combination of vault balances, decimals, and withdraw amount chosen by an attacker-controlled transaction. If that guarantee is violated, `checked_sub` returns `None` and `.unwrap()` panics, aborting the `Withdraw` instruction instead of returning a defined `AmmError`.

### Impact Explanation
Any account holding LP tokens can call `Withdraw` with attacker-chosen `withdraw.amount`; this is a fully permissionless, unprivileged operation. If pool state (vault balances/decimals/accumulated pnl drift from prior swaps) evolves into a configuration where this subtraction underflows, every subsequent `Withdraw` call reaching this line will panic and revert, since the vault/pnl state that produces the underflow is itself a result of normal swap/deposit/withdraw activity and cannot be "fixed" by a single failing transaction. This effectively freezes LP withdrawals for the pool (permanent denial of the `Withdraw` instruction), matching the CVSS vector class of the original CVE (local, low-complexity, no confidentiality/integrity impact, high availability impact).

### Likelihood Explanation
Every other fallible arithmetic operation in the surrounding function correctly propagates errors via `?` (e.g., `ok_or(AmmError::CalculationExRateFailure)?` for `coin_amount`/`pc_amount`), but the pnl-tracking update a few lines later reverts to `.unwrap()`. This inconsistency, combined with the fact that `x1`/`y1` and `coin_amount`/`pc_amount` are computed through independent rounding paths, makes it plausible that adversarial sequences of swaps/deposits/withdraws (attacker fully controls the `Withdraw` transaction's `amount` and can also drive intervening swaps) can drift the pool into an underflow state. However, I was not able to fully derive within this session a concrete numeric sequence proving the underflow is reachable under the specific `calc_take_pnl` invariant bounds — this requires deeper analysis of `Calculator::calc_total_without_take_pnl_no_orderbook` and `calc_take_pnl`'s bounding logic in `math.rs`, which I could not fully trace in the time available.

### Recommendation
Replace the `.unwrap()` calls in the `target_orders.calc_pnl_x`/`calc_pnl_y` update (`program/src/processor.rs` lines 1819-1838, and the analogous block for `process_withdraw_pnl`) with `.ok_or(AmmError::CalculationExRateFailure)?` (or a dedicated error variant), consistent with the handling used for `coin_amount`/`pc_amount` a few lines above, so that an unexpected precision/rounding mismatch produces a defined program error instead of a panic that could permanently block withdrawals for a pool.

### Proof of Concept
Not fully constructible from static analysis alone within this session — reproducing it requires simulating `calc_take_pnl` and `normalize_decimal_v2`/`InvariantPool::exchange_pool_to_token` with adversarial decimals/vault-balance sequences (via repeated swap/deposit/withdraw transactions) to confirm a state where `x1.checked_sub(normalize(pc_amount)).checked_sub(delta_x)` underflows. This would need to be validated with a local test harness (e.g., extending the existing `test_calc_pnl_precision` test in `program/src/processor.rs`) exercising extreme decimal/amount combinations. [3](#0-2) [4](#0-3)

### Citations

**File:** program/src/processor.rs (L1740-1749)
```rust
        if amm.status != AmmStatus::WithdrawOnly.into_u64() {
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
        }
```

**File:** program/src/processor.rs (L1756-1761)
```rust
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1819-1838)
```rust
        target_orders.calc_pnl_x = x1
            .checked_sub(Calculator::normalize_decimal_v2(
                pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_sub(Calculator::normalize_decimal_v2(
                coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
```

**File:** program/src/processor.rs (L3152-3182)
```rust
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)
            .unwrap();
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)
            .unwrap();

        amm.lp_amount = amm.lp_amount.checked_sub(withdraw_lp).unwrap();
        target.calc_pnl_x = x1
            .checked_sub(Calculator::normalize_decimal_v2(
                pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target.calc_pnl_y = y1
            .checked_sub(Calculator::normalize_decimal_v2(
                coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
        total_pc_without_take_pnl = total_pc_without_take_pnl.checked_sub(pc_amount).unwrap();
```
