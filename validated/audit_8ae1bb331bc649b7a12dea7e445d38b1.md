### Title
First-depositor rounding manipulation can permanently brick Deposit/Withdraw/WithdrawPnl via the `calc_take_pnl` invariant check - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` requires that the *current* raw reserve product (`total_pc_without_take_pnl * total_coin_without_take_pnl`) stay `>=` the *stored* snapshot product (`TargetOrders.calc_pnl_x * calc_pnl_y`, restored to native decimals), otherwise it returns `AmmError::CalcPnlError` and the whole instruction reverts. This mirrors the Malda `JumpRateModelV4` bug class: a state value derived from lossy fixed-point math can drift past the value it is checked against, permanently reverting the accrual/settlement path (there, `_accrueInterest`; here, `calc_take_pnl`, called by `Deposit`, `Withdraw`, and `WithdrawPnl`).

### Finding Description
`Calculator::normalize_decimal_v2` and `Calculator::restore_decimal` both use `checked_div`, i.e. floor rounding, when converting between native token decimals and the pool's internal `sys_decimal_value` scale: [1](#0-0) 

On every `Deposit`/`Withdraw`, `target_orders.calc_pnl_x`/`calc_pnl_y` are updated by adding/subtracting a **floored** normalized amount to/from the previous snapshot (`x1`/`y1`), e.g. on withdraw: [2](#0-1) 

Because the amount subtracted on withdraw is rounded down, the stored `calc_pnl_x`/`calc_pnl_y` snapshot can end up systematically *larger* than the true post-withdrawal reserve state. This snapshot is later restored back to native decimals (again with floor rounding) and compared against the live vault balances in `calc_take_pnl`: [3](#0-2) 

If enough of these lossy round-trips accumulate — which is easiest to force in a freshly created, low-liquidity pool where a first depositor controls essentially the entire reserve and rounding error is large relative to the reserve size — the inequality flips permanently: `pool_pc_amount * pool_coin_amount < calc_pc_amount * calc_coin_amount`, and the function falls into the `else` branch, unconditionally returning `AmmError::CalcPnlError`.

`calc_take_pnl` is invoked, unguarded by any fallback, from:
- `process_deposit` (`Deposit` instruction): [4](#0-3) 
- `process_withdraw` (`Withdraw` instruction, unless status is `WithdrawOnly`): [5](#0-4) 
- `process_withdrawpnl` (`WithdrawPnl`): [6](#0-5) 

Once the invariant is violated, every subsequent `Deposit` and `Withdraw` call reverts with `CalcPnlError`, since each call recomputes the same comparison from the same (now permanently skewed) `TargetOrders.calc_pnl_x/y` fields and the pool's actual vault balances — there is no code path that resets or clamps this state.

### Impact Explanation
Once tripped, LPs can no longer call `Withdraw` to redeem their LP tokens for the underlying coin/pc (the pool's core deposit/withdraw functionality freezes), analogous to the "market becomes unresponsive" outcome in the referenced report. This is a permanent freezing of LP funds reachable purely through the in-scope `Deposit`/`Withdraw` instructions with attacker-chosen amounts, no privileged signer required.

### Likelihood Explanation
The floor-rounding drift is deterministic and attacker-controllable: a first depositor picks `pc_decimals`/`coin_decimals`/`sys_decimal_value` combinations (via pool creation) that maximize the decimal-scale mismatch, then performs a sequence of small deposit/withdraw round-trips against a low-liquidity pool they control to accumulate rounding error relative to the (deliberately small) reserve product. This requires only ordinary, unprivileged transactions using `Deposit` and `Withdraw`, making the likelihood realistic for a determined attacker, though it requires several crafted operations rather than a single transaction.

### Recommendation
Avoid a hard, unrecoverable `>=` invariant check whose operands are both derived from floor-rounded fixed-point conversions. Either: (1) bound/clamp the "error" tolerance (e.g., allow a small epsilon or always recompute `calc_pnl_x/y` fresh from current reserves each time rather than incrementally adjusting a stored snapshot with lossy rounding), or (2) round `restore_decimal`/`normalize_decimal_v2` consistently in the direction that biases `calc_pnl_x*calc_pnl_y` to stay `<=` the true reserve product, or (3) make the `else` branch of `calc_take_pnl` degrade gracefully (skip pnl-taking for that call) instead of returning a hard error that blocks `Deposit`/`Withdraw`/`WithdrawPnl` entirely.

### Proof of Concept
1. Attacker creates (or targets) a pool with a large scale mismatch between `sys_decimal_value` and `coin_decimals`/`pc_decimals` (e.g. `coin_decimals=9`, `sys_decimal_value=1e6`, as used in the repo's own test at [7](#0-6) ), and becomes the first/dominant LP with minimal reserves.
2. Attacker repeatedly calls `Deposit` then `Withdraw` with small amounts. Each `Withdraw` subtracts `normalize_decimal_v2(pc_amount/coin_amount)` (floored) from the stored `calc_pnl_x`/`calc_pnl_y` snapshot (`program/src/processor.rs:1818-1838`), while the true reserves in the vaults decrease by the full un-rounded amount.
3. After enough round-trips, the stored `calc_pnl_x*calc_pnl_y` (restored to native decimals) exceeds the true `total_pc_without_take_pnl*total_coin_without_take_pnl`.
4. Any subsequent `Deposit`, `Withdraw`, or `WithdrawPnl` call now hits the `else` branch in `calc_take_pnl` (`program/src/processor.rs:267-278`) and reverts with `AmmError::CalcPnlError` permanently, freezing LP withdrawals for that pool.

### Citations

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

**File:** program/src/processor.rs (L3057-3076)
```rust
    #[test]
    fn test_calc_take_pnl() {
        let mut amm = AmmInfo::default();
        amm.initialize(0, 0, 2, 9, 1000000, 1).unwrap();
        let mut target = TargetOrders::default();
        target.calc_pnl_x = 900000000000000;
        target.calc_pnl_y = 150000000000000000000000000;

        let mut total_pc_without_take_pnl = 1343675125663;
        let mut total_coin_without_take_pnl = 117837534493793;
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
```
