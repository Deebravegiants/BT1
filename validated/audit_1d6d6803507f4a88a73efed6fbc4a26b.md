### Title
Deposit/Withdraw permanently revert instead of gracefully skipping PnL distribution when pool value dips below tracked invariant, freezing LP funds - (File: program/src/processor.rs)

### Summary
`Processor::calc_take_pnl` in `program/src/processor.rs` is the analog of `clearBadDebt`'s `earningsAccumulator` shortfall handling: instead of gracefully degrading when the current pool value can't cover the previously tracked invariant, it hard-fails the whole instruction, which is invoked from the unprivileged `Deposit` and `Withdraw` instructions. [1](#0-0) 

### Finding Description
`calc_take_pnl` computes the "PnL to distribute" by comparing the current pool value (`pool_pc_amount * pool_coin_amount`) against the previously stored invariant (`target.calc_pnl_x * target.calc_pnl_y`, restored from normalized decimals): [2](#0-1) 

If the current product is even marginally smaller than the stored one, the function does not simply skip PnL distribution for that call — it returns `AmmError::CalcPnlError`, aborting the entire instruction: [3](#0-2) 

This mirrors exactly the pattern flagged in the external report: rather than clearing the maximum possible amount (here, simply distributing zero PnL and continuing), the code treats a "less-than" condition as a hard error. The decimal conversions used to build `calc_pnl_x`/`calc_pnl_y` and the live pool amounts (`normalize_decimal_v2`/`restore_decimal`) are lossy, floor-based integer operations: [4](#0-3) 

Because `calc_pnl_x`/`calc_pnl_y` are persisted from one deposit/withdraw call to the next (see the post-update in `process_deposit`/`process_withdraw`), repeated rounding in these decimal conversions can, over time or through crafted dust-sized deposits/withdrawals chosen by an attacker, cause the freshly recomputed `x1*y1` to fall marginally below the stored `calc_pnl_x*calc_pnl_y`. `calc_take_pnl` is called directly inside `process_deposit` and `process_withdraw` — both instructions any unprivileged LP can invoke with attacker-chosen `amount`/`min_*` parameters: [5](#0-4) [6](#0-5) 

Once this state is triggered, every subsequent `Deposit` and `Withdraw` call reverts with `CalcPnlError` (the pool's `AmmStatus` is not automatically changed), because the stale, too-large `calc_pnl_x`/`calc_pnl_y` values in `TargetOrders` are never corrected — there is no code path that resets or partially rolls back this invariant. The only bypass is `process_withdraw`'s special case that skips `calc_take_pnl` entirely when `amm.status == AmmStatus::WithdrawOnly`, which requires a privileged `SetParams` admin action to flip.

### Impact Explanation
Once `pool_pc_amount * pool_coin_amount < calc_pnl_x * calc_pnl_y` occurs, ordinary LPs cannot deposit or withdraw liquidity through the normal path — every such transaction reverts with `CalcPnlError`. This is a permanent freezing of LP funds for the affected pool until a privileged admin (`amm_owner`/`pnl_owner`) intervenes by switching the pool to `WithdrawOnly` status. Because the trigger condition (rounding-induced shortfall) is reachable purely through unprivileged `Deposit`/`Withdraw` transactions with attacker-chosen amounts, and the resulting failure blocks all subsequent LP operations by design (hard revert rather than graceful skip), this matches the "permanent freezing of user or LP funds" impact class.

### Likelihood Explanation
The likelihood depends on how easily an attacker or natural usage can push the floor-rounded, normalized invariant computation below the stored `calc_pnl_x*calc_pnl_y`. Given the lossy decimal normalization (`normalize_decimal_v2`/`restore_decimal` truncate on every conversion) and that `calc_pnl_x`/`calc_pnl_y` persist and compound rounding across many deposit/withdraw cycles, this is plausible but requires either a long sequence of transactions or carefully chosen dust amounts to manifest — making it a real but not trivially one-shot condition.

### Recommendation
Change `calc_take_pnl` to gracefully skip PnL distribution (return `(0, 0)` deltas and leave `need_take_pnl_*`/`calc_pnl_x`/`calc_pnl_y` unchanged) when `pool_pc_amount * pool_coin_amount < calc_pnl_x * calc_pnl_y`, instead of returning `AmmError::CalcPnlError` and reverting the whole `Deposit`/`Withdraw` instruction. This allows LP deposits/withdrawals to proceed normally even when the tracked invariant momentarily exceeds the live pool value, avoiding a hard freeze of user funds.

### Proof of Concept
1. Over repeated `Deposit`/`Withdraw` calls, floor-based `normalize_decimal_v2`/`restore_decimal` conversions accumulate rounding loss in `calc_pnl_x`/`calc_pnl_y` relative to the true pool token amounts.
2. An attacker (or natural usage) performs a sequence of small deposits/withdrawals with amounts chosen so that after conversion, `total_pc_without_take_pnl * total_coin_without_take_pnl` computed in `process_deposit`/`process_withdraw` becomes marginally smaller than the stored `target.calc_pnl_x * target.calc_pnl_y`.
3. The next call to `calc_take_pnl` hits the `else` branch at [3](#0-2)  and returns `AmmError::CalcPnlError`.
4. Every subsequent `Deposit`/`Withdraw` transaction from any LP now reverts identically, since nothing resets `calc_pnl_x`/`calc_pnl_y` or corrects the discrepancy, freezing LP fund movement until an admin manually sets the pool to `WithdrawOnly` via `SetParams`.

### Citations

**File:** program/src/processor.rs (L178-192)
```rust
        let calc_pc_amount = Calculator::restore_decimal(
            target.calc_pnl_x.into(),
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let calc_coin_amount = Calculator::restore_decimal(
            target.calc_pnl_y.into(),
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L267-278)
```rust
        } else {
            msg!(arrform!(
                LOG_SIZE,
                "calc_take_pnl error x:{}, y:{}, calc_pnl_x:{}, calc_pnl_y:{}",
                x1,
                y1,
                identity(target.calc_pnl_x),
                identity(target.calc_pnl_y)
            )
            .as_str());
            return Err(AmmError::CalcPnlError.into());
        }
```

**File:** program/src/processor.rs (L1166-1174)
```rust
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
        let invariant = InvariantToken {
```

**File:** program/src/processor.rs (L1737-1749)
```rust
        // calc and update pnl
        let mut delta_x: u128 = 0;
        let mut delta_y: u128 = 0;
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

**File:** program/src/math.rs (L96-116)
```rust
    pub fn restore_decimal(val: U128, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**6) -> (1.23*10**9)
        // let ret:u64 = val.checked_mul((10 as u64).pow(native_decimal.into())).unwrap().checked_div(amm.sys_decimal_value).unwrap();
        let ret_mut = val
            .checked_mul(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        let ret = ret_mut.checked_div(sys_decimal_value.into()).unwrap();
        ret
    }

    pub fn normalize_decimal_v2(val: u64, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**9) -> (1.23*10**6)
        //let ret:u64 = val.checked_mul(amm.sys_decimal_value).unwrap().checked_div((10 as u64).pow(native_decimal.into())).unwrap();
        let ret_mut = (U128::from(val))
            .checked_mul(sys_decimal_value.into())
            .unwrap();
        let ret = ret_mut
            .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        ret
    }
```
