## Analysis

The Knox finding describes an unguarded subtraction (`auction.totalContracts - totalContractsSold`) that can underflow and revert when accumulated state grows past a reference bound, permanently DoS'ing a fund-recovery path (`withdraw`). The Raydium AMM program contains a structurally identical pattern in `Processor::calc_take_pnl`.

### Title
Unchecked `.unwrap()` subtraction in `calc_take_pnl()` can panic and permanently DoS `Deposit`/`Withdraw` - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` updates the pool's pnl-reserved amounts and then reduces the "tradable" pool totals with two raw `checked_sub(...).unwrap()` calls, instead of the safe `ok_or(AmmError::CheckedSubOverflow)` pattern used everywhere else in the same accounting chain (e.g. `Calculator::calc_total_without_take_pnl_no_orderbook`). If the computed `pc_pnl_amount`/`coin_pnl_amount` ever exceeds the current `total_pc_without_take_pnl`/`total_coin_without_take_pnl`, the subtraction panics instead of returning a program error.

### Finding Description
`calc_take_pnl` is invoked from both `process_deposit` and `process_withdraw` [1](#0-0) [2](#0-1) , both of which are unprivileged, single-transaction instructions that any LP can invoke with attacker-chosen accounts/data.

Inside `calc_take_pnl`, once the price-growth gate `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount` passes, the function computes `pc_pnl_amount`/`coin_pnl_amount` from a chain of decimal-normalize/restore conversions and fee-ratio multiplications, then subtracts them from the caller-supplied running totals using bare `.unwrap()`: [3](#0-2) 

This is in sharp contrast to the otherwise-careful accounting function that feeds these same totals, which explicitly guards against underflow and returns a typed error instead of panicking: [4](#0-3) 

The `pc_pnl_amount`/`coin_pnl_amount` values are derived through several decimal normalize/restore round-trips (`normalize_decimal_v2`, `restore_decimal`) and are fee-ratio scaled independently of `diff_x`/`diff_y` that feed `delta_x`/`delta_y` [5](#0-4) . Because the outer gate check is performed in `sys_decimal_value`-normalized space while the final subtraction operates on raw native-decimal totals, precision loss across differing `coin_decimals`/`pc_decimals` (an AMM-configurable, attacker-visible parameter set at `Initialize2` time) is not proven to always keep `pc_pnl_amount <= *total_pc_without_take_pnl` and `coin_pnl_amount <= *total_coin_without_take_pnl`. If that invariant is ever violated, the `.unwrap()` on the subtraction panics, aborting the instruction.

### Impact Explanation
A panic here does not simply fail the single transaction — since `amm.state_data.need_take_pnl_pc/coin` are updated in-memory and only committed if the whole instruction succeeds, a genuinely broken invariant would recur deterministically on every subsequent `Deposit` or `Withdraw` call against the same pool (and indirectly affects `WithdrawPnl`, which shares the same `calc_take_pnl` call [6](#0-5) ), since the target-orders pnl checkpoint and pool state driving the computation persist on-chain. This would permanently trap LP funds behind a `Withdraw` instruction that can never complete, matching the "DoS causing fund lock" impact class of the reference report.

### Likelihood Explanation
Reaching the vulnerable branch requires the price-growth gate to pass and the decimal-conversion chain to produce a `pc_pnl_amount`/`coin_pnl_amount` that exceeds the raw pool total — a condition dependent on `coin_decimals`/`pc_decimals` skew, `pnl_numerator/pnl_denominator` configuration, and price movement, all of which are influenced by normal pool activity and pool-creation parameters rather than a privileged actor. It is not a trivially demonstrable one-shot exploit from the available static analysis, but the code path is exercised on every `Deposit`/`Withdraw`, uses `.unwrap()` instead of the checked-error pattern used one function away for equivalent state, and the surrounding code comments show awareness that this computation's correctness is being assumed, not proven.

### Recommendation
Replace both `.unwrap()` calls in `calc_take_pnl` (processor.rs lines 257–262) with `checked_sub(...).ok_or(AmmError::CheckedSubOverflow)?`, consistent with `calc_total_without_take_pnl_no_orderbook`, so that an invariant violation returns a clean program error on the current instruction instead of leaving the possibility of a recurring panic that could brick the pool's deposit/withdraw path.

### Proof of Concept
Not independently reproduced with concrete numeric inputs in this review; the finding is based on static code-path analysis showing the unguarded `.unwrap()` subtractions in `calc_take_pnl` operate on values whose relationship to the subtrahend is only checked in a differently-scaled (`sys_decimal_value`-normalized) space, while the actual subtraction occurs in raw native-decimal space after independent decimal-normalize/restore and fee-ratio transformations, reachable from both `Deposit` and `Withdraw`.

### Citations

**File:** program/src/processor.rs (L211-243)
```rust
            // transfer to token_coin_pnl and token_pc_pnl
            // (x1 -x2) * pnl / sys_decimal_value
            let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
            let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
            delta_x = diff_x
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();
            delta_y = diff_y
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();

            let diff_pc_pnl_amount =
                Calculator::restore_decimal(diff_x, amm.pc_decimals, amm.sys_decimal_value);
            let diff_coin_pnl_amount =
                Calculator::restore_decimal(diff_y, amm.coin_decimals, amm.sys_decimal_value);
            let pc_pnl_amount = diff_pc_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
            let coin_pnl_amount = diff_coin_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
```

**File:** program/src/processor.rs (L256-262)
```rust
                // step3: update total_coin and total_pc without pnl
                *total_pc_without_take_pnl = (*total_pc_without_take_pnl)
                    .checked_sub(pc_pnl_amount)
                    .unwrap();
                *total_coin_without_take_pnl = (*total_coin_without_take_pnl)
                    .checked_sub(coin_pnl_amount)
                    .unwrap();
```

**File:** program/src/processor.rs (L1166-1173)
```rust
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```

**File:** program/src/processor.rs (L1494-1502)
```rust
        // calc and update pnl
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```

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

**File:** program/src/math.rs (L242-249)
```rust
    ) -> Result<(u64, u64), AmmError> {
        let total_pc_without_take_pnl = pc_amount
            .checked_sub(amm.state_data.need_take_pnl_pc)
            .ok_or(AmmError::CheckedSubOverflow)?;
        let total_coin_without_take_pnl = coin_amount
            .checked_sub(amm.state_data.need_take_pnl_coin)
            .ok_or(AmmError::CheckedSubOverflow)?;
        Ok((total_pc_without_take_pnl, total_coin_without_take_pnl))
```
