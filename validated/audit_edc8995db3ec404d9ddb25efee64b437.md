### Title
Panics from `.unwrap()` on `checked_sub` in `calc_take_pnl` PnL math can be triggered by ordinary swap activity, permanently bricking Deposit/Withdraw and freezing LP funds - (File: `program/src/processor.rs`, function `Processor::calc_take_pnl`)

### Summary
`Processor::calc_take_pnl` computes the AMM's "take profit" split using an integer square-root approximation and then subtracts the result from the current pool totals with `checked_sub(...).unwrap()`. Because the square-root branch operates on decimal-normalized values (`Calculator::normalize_decimal_v2`, which truncates) while the gating comparison a few lines above operates on native (restored) amounts, the two code paths can disagree once enough swaps/deposits/withdrawals have nudged the pool reserves and `TargetOrders.calc_pnl_x/calc_pnl_y` state through many truncating round-trips. When that happens, the computed `x2`/`y2` "after pnl" values can exceed the current normalized totals `x1`/`y1`, and the unconditional `.unwrap()` on `x1.checked_sub(x2)` / `y1.checked_sub(y2)` panics instead of returning a graceful `AmmError`.

### Finding Description
`calc_take_pnl` is invoked from every ordinary, unprivileged-reachable liquidity path:
- `process_deposit` [1](#0-0) 
- `process_withdraw` (whenever status is not `WithdrawOnly`) [2](#0-1) 
- `process_withdrawpnl` [3](#0-2) 

Inside `calc_take_pnl`, the gating check compares *native* restored amounts: [4](#0-3) 

but the actual pnl-split math that follows operates on *decimal-normalized* values (`x1`, `y1`, `target.calc_pnl_x`, `target.calc_pnl_y`), computing an integer square root and then unconditionally subtracting: [5](#0-4) 

`x1`/`y1` themselves are produced by `Calculator::normalize_decimal_v2`, a floor-division/truncating conversion: [6](#0-5) 

`target.calc_pnl_x`/`calc_pnl_y` are persisted across calls using the same truncating normalization, so truncation error accumulates over repeated deposit/withdraw/swap cycles (this is compounded when `pc_decimals != coin_decimals`, which is common). Once accumulated rounding drift causes `integer_sqrt(x2_power)` to round up past `x1` (or the derived `y2` past `y1`), the `checked_sub(...).unwrap()` calls at line 213/214 panic. Since the panic occurs unconditionally in the pnl-accounting helper shared by Deposit, Withdraw, and WithdrawPnl, and since normal Withdraw cannot avoid calling `calc_take_pnl` unless the pool is already in the privileged `WithdrawOnly` status set by an admin, an unprivileged attacker who drives the pool into this drifted state via ordinary swaps can cause every subsequent Deposit and Withdraw instruction to abort with a Rust panic, with no code path to self-recover the stored `calc_pnl_x`/`calc_pnl_y` state without a privileged status change.

### Impact Explanation
If triggered, the panic causes every future `Deposit`/`Withdraw` transaction against the pool to fail, since the corrupted `TargetOrders.calc_pnl_x`/`calc_pnl_y` values persist in on-chain state and are re-used on every call. Regular LPs lose the ability to withdraw their liquidity through the normal instruction path, which constitutes a permanent freezing of LP funds until a privileged admin action (e.g., forcing `AmmStatus::WithdrawOnly` via `SetParams`) intervenes — mirroring the CVE-2018-3061 bug class where routine, attacker-reachable operations trigger a reliably repeatable crash/hang of a core data-manipulation code path.

### Likelihood Explanation
The trigger condition depends on the interaction between two different rounding domains (native vs. sys_decimal_value-normalized) that are both fully attacker-influenceable through unprivileged swap/deposit/withdraw calls with attacker-chosen `amount_in`/`amount_out`. No signer other than the ordinary swapper/LP is required, and every relevant account (`amm_info`, vault accounts, `TargetOrders`) is validated only for identity/ownership, not for the internal numeric consistency the panic depends on. This makes the condition reachable purely through repeated, low-cost transactions rather than any privileged or off-chain action.

### Recommendation
Replace the unconditional `.unwrap()` calls in `calc_take_pnl` (`x1.checked_sub(x2)`, `y1.checked_sub(y2)`, and the related `checked_mul/div` chains) with `.ok_or(AmmError::CalcPnlError)?` (or `saturating_sub`) so that a rounding-drift condition returns a normal program error instead of panicking, and audit `normalize_decimal_v2`/`restore_decimal` round-trips to ensure the gating comparison and the sqrt-based split always operate in the same unit domain to prevent the drift from arising in the first place.

### Proof of Concept
1. Create a pool with asymmetric `pc_decimals`/`coin_decimals` (e.g., 6 and 9), which maximizes truncation loss per `normalize_decimal_v2`/`restore_decimal` round trip.
2. Repeatedly execute `SwapBaseIn`/`SwapBaseOut` and `Deposit`/`Withdraw` with adversarially chosen small amounts designed to shift the coin:pc ratio asymmetrically each time `calc_take_pnl` updates `target_orders.calc_pnl_x`/`calc_pnl_y` (see the update logic reusing normalized/truncated values at [7](#0-6) ).
3. After sufficient iterations, the accumulated truncation causes `integer_sqrt(x2_power)` (computed from stale `calc_pnl_x/calc_pnl_y`) to exceed the freshly computed `x1`, so the next `Deposit` or `Withdraw` call panics at `x1.checked_sub(x2).unwrap()` in `calc_take_pnl`, aborting the transaction and leaving the pool unusable for ordinary withdrawal until an admin forces `WithdrawOnly` status.

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

**File:** program/src/math.rs (L106-116)
```rust
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
