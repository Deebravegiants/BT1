## Title
Reachable division-by-zero panic in `calc_take_pnl` crashes `Deposit`/`Withdraw`/`WithdrawPnl` transactions - (File: `program/src/processor.rs`, function `calc_take_pnl`; helper `program/src/math.rs`, `Calculator::calc_x_power`)

### Summary
The advisory describes a Go image library that panics on an unchecked, attacker-influenced zero value (zero-width image) reaching an indexing/arithmetic operation. The equivalent bug class in this Rust on-chain program is an unchecked `.unwrap()` on `checked_div`/`checked_mul` where the divisor can legitimately be zero because it derives directly from live pool state (vault balances minus already-accrued PnL). Rust's `Option::unwrap()` panicking on `None` is functionally the same "unchecked assumption about input size/shape leads to a runtime abort" class as an out-of-range index panic.

### Finding Description
`Processor::calc_take_pnl` computes:
```rust
let x2_power = Calculator::calc_x_power(target.calc_pnl_x.into(), target.calc_pnl_y.into(), x1, y1);
let x2 = x2_power.integer_sqrt();
let y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap();
``` [1](#0-0) 

`x1` here is `normalize_decimal_v2(total_pc_without_take_pnl, ...)`, and `total_pc_without_take_pnl` is computed as `pc_vault.amount - amm.state_data.need_take_pnl_pc` with a `checked_sub` guard against underflow, but nothing prevents the result from being exactly `0`: [2](#0-1) 

The gating condition before the division,
```rust
if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
    >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
``` [3](#0-2) 
does not protect against `x1 == 0`: when `pool_pc_amount` (derived from `x1`) is `0`, the left side is `0`, and the branch is still entered whenever `target.calc_pnl_x * target.calc_pnl_y` (the right side) is also `0`. `calc_pnl_x`/`calc_pnl_y` are themselves derived and updated on every `Deposit`/`Withdraw`/`WithdrawPnl` call: [4](#0-3) [5](#0-4) [6](#0-5) 
so an unprivileged actor performing a sequence of ordinary deposits/withdraws/swaps can drive `calc_pnl_x` (or `calc_pnl_y`) toward `0` while simultaneously reducing the live pool balance so that `total_pc_without_take_pnl` (hence `x1`) is `0` on the next `Deposit`/`Withdraw`/`WithdrawPnl` call. When both conditions align, `calc_x_power` produces `0`, `x2 = sqrt(0) = 0`, and `y2 = 0.checked_mul(y1).unwrap().checked_div(x1).unwrap()` divides by `x1 == 0`, causing `checked_div` to return `None` and the subsequent `.unwrap()` to panic. `calc_take_pnl` is invoked from `process_deposit`, `process_withdraw`, and `process_withdrawpnl`, all of which are reachable by any signer submitting a single transaction with attacker-chosen (but validity-checked) accounts: [7](#0-6) [8](#0-7) 

### Impact Explanation
An on-chain panic aborts the entire transaction (compute-unit consumed, all state changes for that transaction reverted) rather than returning a graceful `ProgramError`. If a griefer can reliably steer the pool into this state, they can repeatedly cause failed `Deposit`/`Withdraw`/`WithdrawPnl` transactions for themselves or, more importantly, make the pool itself enter a persistently panicking state so that legitimate LPs' `Withdraw`/`WithdrawPnl` calls also abort — effectively **freezing LP funds** (LPs cannot withdraw liquidity/PnL) until state is manually remediated. This matches the "permanent freezing of user or LP funds" impact bar. Severity is bounded by the difficulty of steering `calc_pnl_x`/`calc_pnl_y` and `total_pc_without_take_pnl` to exactly `0` simultaneously through ordinary fee-bearing swap/deposit/withdraw arithmetic, which is a nontrivial multi-step, precision-dependent path rather than a single-instruction trigger.

### Likelihood Explanation
Medium-low: reaching the exact zero-divisor state requires driving both `total_pc_without_take_pnl` (a vault-balance-derived quantity, only reducible by `1` short of zero within a single swap due to the `amount_out < total_..._without_take_pnl` check in swap instructions) and `target_orders.calc_pnl_x`/`calc_pnl_y` to zero at the same moment, coordinated across multiple `Deposit`/`Withdraw`/`Swap` calls. It is reachable purely by an unprivileged user with attacker-chosen transaction sequences and no special validator/administrative privilege, but it is not a single-transaction, single-instruction trigger like the original zero-width-image bug.

### Recommendation
- In `Calculator::calc_x_power` and the `y2` computation in `calc_take_pnl`, replace the blind `.checked_div(x1).unwrap()` with an explicit zero-check that returns `AmmError::CalcPnlError` (or equivalent) instead of panicking, mirroring the upstream ZPLGFA fix of validating image width before array indexing.
- Tighten the pnl-take gating condition in `calc_take_pnl` (`program/src/processor.rs:188-192`) so that the branch is only entered when `x1 > 0` and `y1 > 0` (not just when the multiplied totals compare favorably), since `0 >= 0` is a degenerate pass-through that should be treated as "no pnl to take" rather than proceeding into the division.
- Add unit/fuzz tests exercising `Deposit`, `Withdraw`, and `WithdrawPnl` at pool states where vault balances minus `need_take_pnl_*` equal zero, to catch regressions.

### Proof of Concept
Conceptual sequence (exact numeric steps require iterative fee/precision modeling, not verified end-to-end in this review):
1. Attacker/LP performs repeated `SwapBaseIn`/`SwapBaseOut` operations, each constrained by `amount_out < total_pc_without_take_pnl`, to reduce `amm_pc_vault.amount` down to a value equal to `amm.state_data.need_take_pnl_pc` (making `total_pc_without_take_pnl == 0` on the next non-swap call).
2. In parallel, prior `Deposit`/`Withdraw` calls have already driven `target_orders.calc_pnl_x` toward `0` via the `checked_sub` updates at `program/src/processor.rs:1352-1371` and `:1818-1838`.
3. Attacker then calls `Deposit`, `Withdraw`, or `WithdrawPnl` on this pool. `calc_take_pnl` computes `x1 == 0`, the gating check `0 >= calc_pnl_x*calc_pnl_y` passes (since `calc_pnl_x≈0`), and `y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap()` panics on division by zero, aborting the transaction — and repeating for any subsequent LP `Withdraw`/`WithdrawPnl` attempt on the pool while state remains in this configuration. [1](#0-0) [2](#0-1)

### Citations

**File:** program/src/processor.rs (L188-192)
```rust
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L199-209)
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
```

**File:** program/src/processor.rs (L1145-1173)
```rust
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
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

**File:** program/src/processor.rs (L1352-1371)
```rust
        target_orders.calc_pnl_x = x1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
```

**File:** program/src/processor.rs (L1495-1502)
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

**File:** program/src/processor.rs (L1531-1532)
```rust
            target_orders.calc_pnl_x = x1.checked_sub(U128::from(delta_x)).unwrap().as_u128();
            target_orders.calc_pnl_y = y1.checked_sub(U128::from(delta_y)).unwrap().as_u128();
```

**File:** program/src/processor.rs (L1818-1838)
```rust
        // step4: update target_orders.calc_pnl_x & target_orders.calc_pnl_y
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

**File:** program/src/math.rs (L238-250)
```rust
    pub fn calc_total_without_take_pnl_no_orderbook<'a>(
        pc_amount: u64,
        coin_amount: u64,
        amm: &'a AmmInfo,
    ) -> Result<(u64, u64), AmmError> {
        let total_pc_without_take_pnl = pc_amount
            .checked_sub(amm.state_data.need_take_pnl_pc)
            .ok_or(AmmError::CheckedSubOverflow)?;
        let total_coin_without_take_pnl = coin_amount
            .checked_sub(amm.state_data.need_take_pnl_coin)
            .ok_or(AmmError::CheckedSubOverflow)?;
        Ok((total_pc_without_take_pnl, total_coin_without_take_pnl))
    }
```
