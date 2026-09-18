### Title
Reachable panic in `calc_take_pnl` via integer-sqrt rounding can permanently freeze deposits/withdrawals/swaps - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` uses raw `.unwrap()` on `checked_sub` calls when deriving the "post take-pnl" pool balances (`x2`, `y2`) from an integer-square-root computation. Because `x2`/`y2` are approximations (truncated `integer_sqrt`), they are not guaranteed to be `<= x1`/`y1` in all pool states, so the subtraction can underflow and panic instead of returning a `ProgramError`. This mirrors the CVE-2018-1000037 bug class (reachable assertion/panic in a parser/calculation routine triggered by attacker-influenced input causing a crash instead of a graceful error), except here the “crash” is a Solana program panic that aborts the transaction for every caller of the pool's core instructions.

### Finding Description
`calc_take_pnl` is invoked from `process_deposit`, `process_withdraw`, `process_withdrawpnl`, and both swap paths whenever the branch condition `pool_pc*pool_coin >= calc_pnl_x*calc_pnl_y` is true [1](#0-0) . Inside that branch it computes `x2` via `calc_x_power(...).integer_sqrt()` and then unconditionally unwraps the subtraction `x1.checked_sub(x2).unwrap()` and `y1.checked_sub(y2).unwrap()`: [2](#0-1) 

`x2` is only an integer-square-root approximation of `sqrt(last_k * current_price)`, and `y2 = x2 * y1 / x1` is a further truncated division [3](#0-2) . Truncation/rounding in `integer_sqrt` and the subsequent multiply-divide means `x2` (or `y2`) can end up numerically larger than `x1` (or `y1`) for certain pool ratios/decimal configurations, even though the outer guard condition passed. When that happens, `checked_sub(...).unwrap()` panics rather than propagating a `ProgramError`, aborting the transaction with a runtime panic instead of a controlled error path.

Every downstream instruction that reaches this code — `Deposit`, `Withdraw`, `WithdrawPnl`, `SwapBaseIn/Out` (and their V2 variants) — calls `calc_take_pnl` unconditionally as part of normal PnL accounting [4](#0-3) [5](#0-4) [6](#0-5) . Because these are the pool's core swap/deposit/withdraw entry points and are reached from a single unprivileged transaction with attacker-influenced amounts (any user picks `amount_in`/`amount_out`/`max_coin_amount` etc., which move the vault balances that feed into `x1`/`y1`), an attacker can, through a sequence of swaps/deposits that shift the pool's `total_pc/total_coin` ratio relative to the stored `target_orders.calc_pnl_x/calc_pnl_y`, drive the pool into a state where `x2 > x1` (or `y2 > y1`), causing every subsequent Deposit/Withdraw/Swap call on that pool to panic and fail.

### Impact Explanation
If the pool enters the panic-triggering state, `calc_take_pnl` will panic on **every** call, and since that function runs inside `process_deposit`, `process_withdraw`, `process_withdrawpnl`, and both swap directions, the pool becomes permanently unusable: LPs can no longer withdraw their liquidity and swappers can no longer trade against it. This is a permanent freezing of user/LP funds — the funds remain in the vaults but become inaccessible through the program's own instruction set, since the only code path that updates `calc_pnl_x`/`calc_pnl_y` (which could rebalance the state) is this same panicking function.

### Likelihood Explanation
Reachability requires only that an unprivileged user submit ordinary Deposit/Withdraw/Swap transactions that shift the coin/pc vault ratio relative to the recorded PnL baseline — no special account permissions or crafted account data are needed, only crafted trade sizes/sequences. The exact numeric conditions that trigger `x2 > x1` depend on decimal normalization, fee ratios and specific integer rounding of `integer_sqrt`/`checked_div`, so triggering it deterministically requires numeric analysis or fuzzing of the rounding boundary rather than a single obvious input; the existing unit tests (`test_calc_take_pnl`, `test_calc_pnl_precision`) only exercise "normal" values, and none assert the invariant `x2 <= x1` under adversarial ratios, which is consistent with this rounding edge case not having been hardened against.

### Recommendation
Replace the `.unwrap()` calls on `x1.checked_sub(x2)` and `y1.checked_sub(y2)` in `calc_take_pnl` with `checked_sub(...).ok_or(AmmError::CalcPnlError)?` (or clamp `x2`/`y2` to at most `x1`/`y1` before subtracting), so that a rounding-induced inconsistency returns a normal `ProgramError` instead of panicking, and add an explicit invariant check/test verifying `x2 <= x1` and `y2 <= y1` for boundary ratios before performing the subtraction.

### Proof of Concept
1. Create a pool and perform a sequence of `Deposit`/`Swap` instructions that skew `total_pc_without_take_pnl` / `total_coin_without_take_pnl` (the live vault-derived amounts) relative to the stored `target_orders.calc_pnl_x`/`calc_pnl_y` baseline, while keeping the guard `pool_pc*pool_coin >= calc_pnl_x*calc_pnl_y` satisfied (see gate at `processor.rs:190-192`).
2. Choose amounts/decimals such that the truncated `integer_sqrt` result for `x2` (or the truncated `x2*y1/x1` for `y2`) rounds up past `x1` (or `y1`) — this can be probed offline using the same formulas in `math.rs`/`calc_x_power` with the pool's actual `pc_decimals`, `coin_decimals`, and `sys_decimal_value`.
3. Submit any subsequent `Deposit`, `Withdraw`, `WithdrawPnl`, or swap instruction against the pool; `calc_take_pnl`'s `checked_sub(...).unwrap()` at `processor.rs:213-214` panics, aborting the transaction, and this will recur for all future calls until the pool state is somehow corrected — which normal instructions cannot do since they all route through this same function.

### Citations

**File:** program/src/processor.rs (L188-192)
```rust
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L199-214)
```rust
            let x2_power = Calculator::calc_x_power(
                target.calc_pnl_x.into(),
                target.calc_pnl_y.into(),
                x1,
                y1,
            );
            // let x2 = Calculator::sqrt(x2_power).unwrap();
            let x2 = x2_power.integer_sqrt();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl x2_power:{}, x2:{}", x2_power, x2).as_str());
            let y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl y2:{}", y2).as_str());

            // transfer to token_coin_pnl and token_pc_pnl
            // (x1 -x2) * pnl / sys_decimal_value
            let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
            let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
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

**File:** program/src/processor.rs (L1741-1748)
```rust
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
```
