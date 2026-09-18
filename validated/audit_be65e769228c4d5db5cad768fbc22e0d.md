## Analysis

Mapping the TensorFlow `CHECK`-fail bug class (unchecked shape/dimension math that hits a Rust/C++ `CHECK`/`unwrap()` panic instead of a controlled error) onto Raydium AMM, the closest analog is the pervasive use of `.unwrap()` on `checked_sub`/`checked_mul`/`checked_div` results in `Calculator::calc_take_pnl`, which is reachable from the `Deposit`, `WithdrawPnl`, and `Withdraw` instructions.

### Title
Unchecked-panic (`unwrap()`-on-`checked_sub`) in `calc_take_pnl` permanently freezes Deposit/Withdraw once pool state drifts — analogous to TensorFlow `SparseConcat` CHECK-fail (BIT-tensorflow-2021-29534) - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` computes `x2`/`y2` (the "after take-pnl" invariant point) and then does `x1.checked_sub(x2).unwrap()` / `y1.checked_sub(y2).unwrap()` without any fallback error path, exactly the pattern flagged in the TensorFlow report: a legacy/unchecked arithmetic primitive that aborts the whole execution (a `CHECK`-fail / Rust panic) instead of returning a `Result` error when the assumed invariant (`x2 <= x1`, `y2 <= y1`) does not hold. [1](#0-0) 

### Finding Description
`calc_take_pnl` only checks `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount` (the k-invariant) before computing `x2 = sqrt(last_x*last_y*current_x/current_y)` and `y2 = x2*y1/x1`. [2](#0-1) 

That k-check does **not** guarantee `x2 <= x1` and `y2 <= y1` individually — it only bounds the product. If the pool's coin/pc ratio has drifted (via ordinary swaps that legitimately change `current_x`/`current_y` relative to the stored `target.calc_pnl_x`/`calc_pnl_y` baseline) such that `x2 > x1` or `y2 > y1` while the product invariant still holds, the subsequent line panics:
```rust
let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
``` [3](#0-2) 

This is functionally the same class of bug as the TensorFlow report: an internal helper takes attacker-influenced inputs, performs an assumption-based computation, and then calls an infallible/panicking primitive (`unwrap()` here, `CHECK` there) instead of propagating a typed error — turning a data-dependent edge case into an unconditional abort of the calling instruction.

Crucially, `calc_take_pnl` is invoked from every LP-liquidity-affecting instruction reachable by ordinary users:
- `process_deposit` (Deposit) [4](#0-3) 
- `process_withdrawpnl` (WithdrawPnl) [5](#0-4) 
- `process_withdraw` (Withdraw, whenever `amm.status != WithdrawOnly`) [6](#0-5) 

Because the panic condition depends only on pool state (`x1`,`y1` derived from live vault balances, and `target.calc_pnl_x`/`calc_pnl_y` which are themselves updated by every prior Deposit/Withdraw call using the same unwrap-laden arithmetic), once the state enters the panicking region, **all** future calls to Deposit, WithdrawPnl, and Withdraw for that pool will panic and revert, since none of them can get past `calc_take_pnl` to update state out of the bad region.

### Impact Explanation
If reachable, this permanently freezes LP deposit and withdrawal functionality for the affected pool: LPs would be unable to withdraw their underlying coin/pc tokens (funds permanently locked), and no new deposits could be processed either, since both code paths call the same panicking function. This matches the "permanent freezing of user or LP funds" impact bar.

### Likelihood Explanation
This requires demonstrating a concrete state transition sequence (via legitimate swaps and deposits/withdrawals, no privileged signer needed) where `pool_pc*pool_coin >= calc_pnl_x*calc_pnl_y` holds while `x2 > x1` or `y2 > y1` individually — i.e., a case where the k-invariant guard is insufficient to prevent the underflow. This is plausible given the guard only checks the product, not the individual components, but confirming an exact triggering sequence requires numerical/fuzzing analysis of `calc_x_power`/`integer_sqrt` behavior under decimal-normalized values across the various `pc_decimals`/`coin_decimals` combinations, which is beyond what can be conclusively proven via static code reading alone.

### Recommendation
Replace the `.unwrap()` calls on `x1.checked_sub(x2)` and `y1.checked_sub(y2)` (and the other `.unwrap()`s in `calc_take_pnl`) with `.ok_or(AmmError::CheckedSubOverflow)?` (or equivalent), returning a proper `AmmError` instead of panicking, and add an explicit invariant check (`x2 <= x1 && y2 <= y1`) before computing the deltas so that a benign error is returned rather than an unrecoverable panic that could brick the pool's Deposit/Withdraw path.

### Proof of Concept
A concrete numeric PoC (a sequence of `Initialize2` → attacker-driven `SwapBaseIn`/`SwapBaseOut` calls that skew `current_x`/`current_y` relative to `target.calc_pnl_x`/`calc_pnl_y`, followed by a `Deposit` or `Withdraw`) would be needed to conclusively trigger `x1.checked_sub(x2).unwrap()` panicking; this was not constructed/verified here, so this should be treated as an analog worth investigating with a fuzz/property test against `Processor::calc_take_pnl` and `Calculator::calc_x_power` rather than a confirmed exploit. [7](#0-6)

### Citations

**File:** program/src/processor.rs (L188-214)
```rust
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
            // last k is
            // let last_k: u128 = (target.calc_pnl_x as u128).checked_mul(target.calc_pnl_y as u128).unwrap();
            // current k is
            // let current_k: u128 = (x1 as u128).checked_mul(y1 as u128).unwrap();
            // current p is
            // let current_p: u128 = (x1 as u128).checked_div(y1 as u128).unwrap();
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

**File:** program/src/processor.rs (L1494-1495)
```rust
        // calc and update pnl
        let (delta_x, delta_y) = Self::calc_take_pnl(
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

**File:** program/src/math.rs (L50-60)
```rust
    pub fn calc_x_power(last_x: U256, last_y: U256, current_x: U256, current_y: U256) -> U256 {
        // must be use u256, because u128 may be overflow
        let x_power = last_x
            .checked_mul(last_y)
            .unwrap()
            .checked_mul(current_x)
            .unwrap()
            .checked_div(current_y)
            .unwrap();
        x_power
    }
```
