## Title
`calc_take_pnl` can permanently revert `Withdraw`/`WithdrawPnl`, freezing LP funds until a privileged status change - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` performs an invariant sanity check (`pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount`) before computing PnL, and returns `Err(AmmError::CalcPnlError)` when it fails [1](#0-0) . This function is invoked unconditionally inside `process_withdraw` whenever `amm.status != AmmStatus::WithdrawOnly` [2](#0-1) , and unconditionally inside `process_withdrawpnl` [3](#0-2) . This is directly analogous to the `initVaultCache` liveness issue in the report: an accounting/bookkeeping computation (PnL snapshot vs. current invariant, analogous to the interest accumulator) can revert, and that revert blocks the otherwise-unrelated core operation (`withdraw`) that users must always be able to perform.

### Finding Description
`calc_take_pnl` compares the *current* pool invariant (`total_pc_without_take_pnl * total_coin_without_take_pnl`, in raw token units) against a *snapshot* invariant restored from `target_orders.calc_pnl_x`/`calc_pnl_y` (values recorded the last time PnL was taken, converted through `normalize_decimal_v2`/`restore_decimal`) [4](#0-3) . Because `normalize_decimal`/`restore_decimal` use floor/ceiling integer division when converting between "system decimals" and native token decimals [5](#0-4) , and because ordinary swaps continuously update `total_pc_without_take_pnl`/`total_coin_without_take_pnl` while `calc_pnl_x`/`calc_pnl_y` are only refreshed on deposit/withdraw/`withdrawpnl` [6](#0-5) , repeated normal swap activity accumulates rounding drift between the two sides of the comparison. Once enough drift accrues (or a sequence of swaps is crafted to push the raw-unit product just under the recorded snapshot product), the `>=` check fails and `calc_take_pnl` returns `AmmError::CalcPnlError` instead of completing.

Both `process_withdraw` (outside of the privileged `WithdrawOnly` status) and `process_withdrawpnl` call `calc_take_pnl` unconditionally as a precondition to performing the withdrawal accounting [7](#0-6) [8](#0-7) . If the error is returned, the entire instruction reverts — the LP token holder cannot redeem their share of the pool. The only escape hatch is the `AmmStatus::WithdrawOnly` bypass, which is set exclusively by the AMM owner/config authority via `SetParams`, a privileged action outside the reach of an ordinary swapper or LP.

This mirrors the reported Cache.sol pattern precisely: a secondary bookkeeping computation (interest accumulator vs. PnL invariant snapshot) is allowed to hard-fail, and that hard failure is wired directly into the path that must remain live for users to exit their position (`withdraw`/`redeem`/`liquidate` in the original report vs. `Withdraw`/`WithdrawPnl` here).

### Impact Explanation
If the `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount` check fails, every subsequent call to `Withdraw` (while status is not `WithdrawOnly`) and `WithdrawPnl` reverts with `CalcPnlError`. LPs are unable to withdraw their underlying coin/pc tokens; their liquidity is frozen until the AMM's privileged owner explicitly sets the pool to `WithdrawOnly` status via `SetParams`. This is a freezing-of-funds condition triggerable through unprivileged, ordinary swap transactions, satisfying the "permanent freezing of user or LP funds" bar for Medium/High severity.

### Likelihood Explanation
The condition depends on accumulated decimal-rounding drift between `calc_pnl_x`/`calc_pnl_y` (updated only on deposit/withdraw events) and the live vault balances (updated on every swap) across `normalize_decimal_v2`/`restore_decimal` conversions with floor rounding [9](#0-8) . Pools with mismatched coin/pc decimals and heavy one-sided swap activity between PnL-taking events are the most susceptible; an attacker fully controls the swap direction/amount sequence of their own transactions and can bias rounding to accelerate reaching the failing branch.

### Recommendation
`calc_take_pnl` should not be able to block basic withdrawal of principal. Decouple the PnL-snapshot sanity check from the core withdraw path: if the invariant-drift check fails, skip/no-op the PnL adjustment (treat `delta_x = delta_y = 0`) rather than returning a hard error that reverts the whole `Withdraw`/`WithdrawPnl` instruction, so LPs can always redeem their share of the pool regardless of the state of unrelated PnL bookkeeping.

### Proof of Concept
1. Create a pool via `Initialize2` with coin/pc mints of different decimal precisions (e.g. coin_decimals=9, pc_decimals=6) so `normalize_decimal_v2`/`restore_decimal` conversions round non-trivially [10](#0-9) .
2. Perform an initial `Deposit`/`Withdraw` cycle so `target_orders.calc_pnl_x`/`calc_pnl_y` are set from a snapshot at time T0 [6](#0-5) .
3. Submit a sequence of `SwapBaseIn`/`SwapBaseOut` transactions (attacker fully controls direction and amounts) that move `total_pc_without_take_pnl`/`total_coin_without_take_pnl` in a way that accumulates floor-rounding loss relative to the fixed `calc_pnl_x`/`calc_pnl_y` snapshot, until `pool_pc_amount * pool_coin_amount < calc_pc_amount * calc_coin_amount` in raw units.
4. Call `Withdraw` (pool not in `WithdrawOnly` status) or `WithdrawPnl`: the call reaches `calc_take_pnl` [11](#0-10) , the invariant check fails, and the instruction returns `AmmError::CalcPnlError`, reverting the transaction and leaving the LP unable to withdraw until the privileged owner sets `AmmStatus::WithdrawOnly`.

### Citations

**File:** program/src/processor.rs (L167-198)
```rust
    pub fn calc_take_pnl(
        target: &TargetOrders,
        amm: &mut AmmInfo,
        total_pc_without_take_pnl: &mut u64,
        total_coin_without_take_pnl: &mut u64,
        x1: U256,
        y1: U256,
    ) -> Result<(u128, u128), ProgramError> {
        // calc pnl
        let mut delta_x: u128;
        let mut delta_y: u128;
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
            // last k is
            // let last_k: u128 = (target.calc_pnl_x as u128).checked_mul(target.calc_pnl_y as u128).unwrap();
            // current k is
            // let current_k: u128 = (x1 as u128).checked_mul(y1 as u128).unwrap();
            // current p is
            // let current_p: u128 = (x1 as u128).checked_div(y1 as u128).unwrap();
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

**File:** program/src/processor.rs (L1494-1503)
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
        msg!(arrform!(LOG_SIZE, "withdrawpnl total_pc:{}, total_pc:{}, delta_x:{}, delta_y:{}, need_take_coin:{}, need_take_pc:{}",total_pc_without_take_pnl, total_coin_without_take_pnl, delta_x, delta_y, identity(amm.state_data.need_take_pnl_coin), identity(amm.state_data.need_take_pnl_pc)).as_str());
```

**File:** program/src/processor.rs (L1738-1749)
```rust
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

**File:** program/src/math.rs (L80-116)
```rust
    pub fn normalize_decimal(val: u64, native_decimal: u64, sys_decimal_value: u64) -> u64 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**9) -> (1.23*10**6)
        //let ret:u64 = val.checked_mul(amm.sys_decimal_value).unwrap().checked_div((10 as u64).pow(native_decimal.into())).unwrap();
        let ret_mut = (U128::from(val))
            .checked_mul(sys_decimal_value.into())
            .unwrap();
        let ret = Self::to_u64(
            ret_mut
                .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
                .unwrap()
                .as_u128(),
        )
        .unwrap();
        ret
    }

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
