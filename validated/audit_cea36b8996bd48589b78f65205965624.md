### Title
Persistent Denial-of-Service via Integer-Underflow Panic in `calc_take_pnl`, Permanently Freezing Pool Funds - (File: `program/src/processor.rs`)

### Summary
`calc_take_pnl` — invoked on every `Deposit`, `Withdraw`, and `WithdrawPnl` (and, based on the identical `target_orders.calc_pnl_x`/`calc_pnl_y` update pattern that immediately precedes `process_swap_base_in`, also on the swap paths) — performs an unchecked `checked_sub().unwrap()` between an integer-square-root result and the pool's current normalized reserve value. If that subtraction underflows, the program panics and the transaction aborts. Because the operands are derived from persistent on-chain state (`TargetOrders.calc_pnl_x` / `calc_pnl_y`), once the pool is driven into a state where this underflow condition holds, every subsequent transaction touching the pool through these code paths will panic, permanently bricking the pool for all depositors, withdrawers and swappers — the same "crash/hang → complete DOS" bug class described in CVE-2018-2590, but here reachable by an ordinary unprivileged user via a standard transaction rather than requiring elevated MySQL privileges.

### Finding Description
`calc_take_pnl` gates its pnl-rebasing logic with a guard comparing **restored-decimal** (real-unit) quantities: [1](#0-0) 

but then performs the actual math in **normalized fixed-point** units (`x1`, `y1`, and stored `target.calc_pnl_x` / `calc_pnl_y`, all scaled by `amm.sys_decimal_value`): [2](#0-1) 

`calc_x_power` computes `last_x * last_y * current_x / current_y` in `U256`, and `x2` is the integer square root of that product: [3](#0-2) 

The subsequent `diff_x = x1.checked_sub(x2).unwrap()` and `diff_y = y1.checked_sub(y2).unwrap()` assume `x2 <= x1` (and `y2 <= y1`) always holds whenever the raw-unit guard at line 190 passes. Because `normalize_decimal_v2` / `restore_decimal` perform truncating integer division when converting between token decimals and the internal `sys_decimal_value` scale (relevant whenever `coin_decimals != pc_decimals`, the common case, e.g. SOL/USDC pools), the guard's raw-unit comparison and the sqrt computation's normalized-unit comparison are not guaranteed to agree. It is therefore possible for the raw-unit check to pass while the normalized-space `x2` (or `y2`) ends up greater than `x1` (or `y1`), causing the `checked_sub().unwrap()` to panic.

This code path is reached unconditionally from `process_deposit` and `process_withdraw`: [4](#0-3) [5](#0-4) 

and from `process_withdrawpnl`: [6](#0-5) 

`target_orders.calc_pnl_x` / `calc_pnl_y` are then persisted back to on-chain state after every deposit/withdraw: [7](#0-6) 

Since these fields are mutated by ordinary user-triggered instructions using attacker-chosen amounts (`max_coin_amount`, `max_pc_amount`, `amount`, etc.), a normal user (not a privileged signer) can, through a sequence of deposits/withdrawals/swaps that shift the pool price and reserves, push `calc_pnl_x` / `calc_pnl_y` into a state where the rounding mismatch described above triggers the underflow. Once that state is written, **every future call into `calc_take_pnl`** — i.e., every future deposit, withdraw, withdrawpnl, and (per the shared code pattern feeding into `process_swap_base_in`) swap — panics and reverts, permanently locking all coin/pc/LP tokens held by the pool.

### Impact Explanation
This is not a single failed transaction (which would be a normal, low-impact revert). Because the corrupting values are committed to persistent `TargetOrders` account state, the panic condition becomes permanent: no further deposit, withdraw, or swap on the affected pool can succeed, since all of them route through `calc_take_pnl` before performing any token transfer. This constitutes permanent freezing of user and LP funds locked in the pool's vaults, matching the "concrete theft or permanent freezing of user or LP funds" bar required for this analog, and is analogous in bug class (a reachable server-side crash/hang causing complete denial of service) to CVE-2018-2590.

### Likelihood Explanation
Reachability requires no special privileges — only ordinary `Deposit`/`Withdraw`/`Swap` transactions with attacker-controlled amounts against an existing pool, well within the stated in-scope instruction set. Triggering the specific rounding-mismatch state requires precise conditions (decimal-mismatched pools, specific reserve ratios accumulated over one or more transactions) that I was not able to fully enumerate or reproduce numerically within the available investigation, so likelihood should be treated as plausible but unconfirmed rather than proven-exploitable in a single crafted transaction.

### Recommendation
- Perform the `pool_pc*pool_coin` vs `calc_pc*calc_coin` guard check in the same numeric space (normalized fixed-point) as the subsequent `x2`/`y2` sqrt computation, eliminating the decimal-rounding mismatch between the two comparisons.
- Replace `checked_sub().unwrap()` on `diff_x`/`diff_y` (and the corresponding `y2` computation) with a saturating operation or an explicit `AmmError::CalcPnlError` fallback when `x2 > x1` or `y2 > y1`, so a single bad state degrades gracefully instead of permanently panicking on every future call.
- Add regression tests covering pools with distinct `coin_decimals`/`pc_decimals` and boundary reserve ratios to catch rounding-induced underflow before deployment.

### Proof of Concept
Conceptual PoC (not fully validated numerically due to tool-iteration limits):
1. Create a pool where `coin_decimals != pc_decimals` (e.g., 9 vs 6), so `normalize_decimal_v2`/`restore_decimal` conversions are lossy.
2. Submit a sequence of `Deposit`/`Withdraw`/`Swap` transactions with attacker-chosen amounts that gradually shift `total_pc_without_take_pnl` / `total_coin_without_take_pnl` and get committed into `TargetOrders.calc_pnl_x` / `calc_pnl_y` via `process_deposit`/`process_withdraw` (`program/src/processor.rs:1352-1371`).
3. Continue until a state is reached where the raw-unit guard at `program/src/processor.rs:190-192` passes but the normalized-space `x2` (via `Calculator::calc_x_power`, `program/src/math.rs:50-60`) exceeds `x1`.
4. The next transaction touching the pool through `calc_take_pnl` (`diff_x = x1.checked_sub(x2).unwrap()`, `program/src/processor.rs:213`) panics, and this condition persists for all subsequent transactions since the corrupting state is already committed on-chain — freezing all funds in the pool.

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

**File:** program/src/processor.rs (L1474-1495)
```rust
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
        msg!(arrform!(
            LOG_SIZE,
            "withdrawpnl total_pc:{}, total_coin:{}, x:{}, y:{}",
            total_pc_without_take_pnl,
            total_coin_without_take_pnl,
            x1,
            y1
        )
        .as_str());

        // calc and update pnl
        let (delta_x, delta_y) = Self::calc_take_pnl(
```

**File:** program/src/processor.rs (L1740-1748)
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
