## Title
Division-by-zero panic in PnL calculation (`calc_take_pnl` / `calc_x_power`) permanently bricks Deposit/Withdraw on a drained pool - ([File: program/src/processor.rs], [File: program/src/math.rs])

### Summary
The external report describes an unauthenticated, unprivileged request that triggers an internal computation which crashes the server (division/format handling bug reachable via ordinary protocol input). The reachable analog in this AMM program is a hard `unwrap()`-on-`checked_div()` panic inside the PnL reconciliation logic that every `Deposit` and `Withdraw` call executes. When the pool's tracked reserves (`total_pc_without_take_pnl` / `total_coin_without_take_pnl`) and the `TargetOrders` PnL trackers (`calc_pnl_x` / `calc_pnl_y`) simultaneously reach zero — an ordinary, unprivileged outcome of normal liquidity draining — any further `Deposit` or `Withdraw` instruction on that pool aborts with a panic, permanently bricking the pool's LP entry/exit path.

### Finding Description
`Processor::calc_take_pnl` is called from `process_deposit` and `process_withdraw` (both reachable by any unprivileged user) with `x1`/`y1` derived from live vault balances: [1](#0-0) 

Inside `calc_take_pnl`, the code guards the risky branch with a product comparison, then computes `calc_x_power` and divides by `current_y` unconditionally once inside the branch: [2](#0-1) 

`calc_x_power` performs an un-guarded `checked_div(current_y).unwrap()`: [3](#0-2) 

and the subsequent `y2` computation performs another un-guarded `checked_div(x1).unwrap()`: [4](#0-3) 

The entry guard `pool_pc_amount.checked_mul(pool_coin_amount) >= calc_pc_amount.checked_mul(calc_coin_amount)` is meant to skip the division path when reserves are zero, but it fails to protect against the case where **both sides are simultaneously zero** (`0 >= 0` is `true`), which is exactly the state a pool converges to once nearly all liquidity has been withdrawn and PnL trackers (`target_orders.calc_pnl_x`/`calc_pnl_y`, updated every `Deposit`/`Withdraw` at) reach zero: [5](#0-4) [6](#0-5) 

Once that zero/zero state is reached (either by a full pool drain, or by residual dust LP holdings after the last large LP exits), every future call to `process_deposit` or `process_withdraw` recomputes `x1=0`, `y1=0`, re-enters the vulnerable branch, and panics on the `checked_div` in `calc_x_power`/`y2`. Since a Solana program panic aborts only the single transaction but the on-chain state that causes the panic (zero reserves + zero PnL trackers) persists permanently, **every subsequent Deposit or Withdraw transaction against that AMM will panic forever**, with no code path able to recover it.

### Impact Explanation
Any remaining dust LP-token holders can never redeem their tokens (`Withdraw` always panics), permanently freezing their share of the vaults' backing tokens. New liquidity providers can never re-seed the pool through `Deposit` either, because the identical panic path is hit. This matches the "permanent freezing of user or LP funds" impact category: user/LP funds already recorded as owed become permanently unredeemable through the normal instruction interface once the pool's internal accounting reaches the zero/zero state.

### Likelihood Explanation
Reaching this state does not require any privileged signer or malicious validator — it is the natural terminal state of a pool whose liquidity is driven toward zero through ordinary sequences of unprivileged `Deposit`/`Withdraw` calls (e.g., a single LP fully or near-fully exiting a low-liquidity pool, or a sequence of small withdrawals rounding the PnL trackers to zero). No special account permissions, signer keys, or off-chain components are needed; the transaction shape (`Withdraw`/`Deposit`, standard accounts) is exactly what is described in `instruction.rs`. That said, precisely converging `total_pc/coin_without_take_pnl` and `target_orders.calc_pnl_x/y` to zero simultaneously (rather than merely near-zero) depends on exact numeric conditions of a given pool's decimal/fee configuration, so likelihood is pool-state-dependent rather than trivially triggerable on every pool at will.

### Recommendation
- In `calc_take_pnl` (`program/src/processor.rs`), explicitly check for `x1 == 0` or `y1 == 0` before entering the PnL-adjustment branch and short-circuit to a zero-delta result (or a defined error) instead of relying on the multiplicative guard.
- In `Calculator::calc_x_power` (`program/src/math.rs`), replace the unchecked `checked_div(current_y).unwrap()` with a checked division that returns a proper `AmmError` (e.g., `AmmError::CalcPnlError`) instead of panicking, matching the error-handling style used elsewhere in the same function.
- Add regression tests that drive a pool to a fully-drained state and assert `Deposit`/`Withdraw` still return a graceful `ProgramError` rather than panicking.

### Proof of Concept
1. Create a low-liquidity pool via `Initialize2`.
2. As the sole LP, submit `Withdraw` instructions progressively removing nearly all liquidity, letting the resulting `total_pc_without_take_pnl`, `total_coin_without_take_pnl`, and `target_orders.calc_pnl_x`/`calc_pnl_y` (updated per `program/src/processor.rs:1819-1838`) converge to `0`.
3. Submit one more unprivileged `Deposit` or `Withdraw` instruction against the same pool.
4. `Processor::calc_take_pnl` is invoked with `x1 = y1 = 0`; the guard at `processor.rs:190-192` evaluates `0 >= 0` as true, entering the branch; `Calculator::calc_x_power` (`math.rs:57-58`) executes `checked_div(current_y=0).unwrap()`, causing a Rust panic and aborting the transaction.
5. Because the on-chain state (`x1=0`, `y1=0`, `calc_pnl_x=0`, `calc_pnl_y=0`) persists, every future `Deposit`/`Withdraw` transaction against this pool reproduces the panic, permanently freezing the instruction path for that AMM.

Note: exact numeric parameters to hit the zero/zero convergence deterministically (accounting for decimals, fees, and rounding) were not traced end-to-end within available tool calls; a background Devin session with test-harness execution (`cargo test`) would be needed to construct and confirm a concrete numeric sequence of `Deposit`/`Withdraw` amounts that triggers the panic exactly, and to validate the proposed fix.

### Citations

**File:** program/src/processor.rs (L188-209)
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
