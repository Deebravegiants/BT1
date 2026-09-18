### Title
Permanent freezing of LP funds via accumulated rounding drift in `calc_pnl_x`/`calc_pnl_y` bookkeeping breaking the `calc_take_pnl` invariant check - (File: `program/src/processor.rs`)

### Summary
`Processor::process_withdraw` and `Processor::process_deposit` update the pool's PnL bookkeeping state (`target_orders.calc_pnl_x`/`calc_pnl_y`, which represent the "last known k" of the pool) by incrementally adding/subtracting floor-rounded token amounts, while the "current k" used to validate that state on every subsequent call is recomputed independently from the real vault balances. Because floor rounding is applied twice on different bases (once on the withdrawn/deposited token amount, once again when it is re-normalized with `normalize_decimal_v2`), the incremental bookkeeping value can drift away from the value that a fresh recomputation from vault balances would produce. If this drift pushes `calc_pnl_x * calc_pnl_y` (last_k) above the real `pool_pc_amount * pool_coin_amount` (current_k), the invariant check in `Processor::calc_take_pnl` fails and returns `AmmError::CalcPnlError` on every future call, permanently blocking `Deposit`, `Withdraw`, and `WithdrawPnl` for that pool.

### Finding Description
`calc_take_pnl` enforces:

```
if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
    >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
{ ... } else { return Err(AmmError::CalcPnlError.into()); }
``` [1](#0-0) 

This function is invoked unconditionally by `process_deposit`, `process_withdraw` (except when `AmmStatus::WithdrawOnly`), and `process_withdrawpnl`: [2](#0-1) [3](#0-2) [4](#0-3) 

After a successful `process_withdraw`, the bookkeeping state is updated by *subtracting* the floor-rounded, re-normalized withdrawn amount from the pre-call `x1`/`y1`:

```rust
target_orders.calc_pnl_x = x1
    .checked_sub(Calculator::normalize_decimal_v2(pc_amount, amm.pc_decimals, amm.sys_decimal_value))
    .unwrap()
    .checked_sub(U128::from(delta_x))
    .unwrap()
    .as_u128();
``` [5](#0-4) 

`pc_amount` itself is already a floor-rounded proportional share of the pool:
```rust
let coin_amount = invariant.exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)...
let pc_amount = invariant.exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)...
``` [6](#0-5) 

`normalize_decimal_v2` performs a second, independent floor division: [7](#0-6) 

The same pattern applies to `process_deposit`, which instead *adds* a similarly double-rounded quantity to the bookkeeping state: [8](#0-7) 

On every call, the "current k" side of the check (`pool_pc_amount`, `pool_coin_amount`) is instead recomputed *fresh* each time directly from real vault balances via `calc_total_without_take_pnl_no_orderbook`: [9](#0-8) 

Because the bookkeeping side accumulates rounding error incrementally across many `Deposit`/`Withdraw` calls while the real-balance side is recomputed from scratch each time (bounded, non-cumulative rounding), repeated deposit/withdraw activity on a pool can drive the tracked `calc_pnl_x * calc_pnl_y` (last_k) to exceed the real `pool_pc_amount * pool_coin_amount` (current_k). This is structurally the same class of bug as the referenced Cooler issue: an assumption that a rounded-down incremental update always stays ≤ (or ≥, depending on direction) a value recomputed fresh from source-of-truth balances, which floor/ceiling rounding silently violates after enough repetitions.

### Impact Explanation
Once `pool_pc_amount * pool_coin_amount < calc_pc_amount * calc_coin_amount`, `calc_take_pnl` unconditionally returns `AmmError::CalcPnlError` and the transaction reverts *before* `target_orders.calc_pnl_x`/`calc_pnl_y` can be corrected — the erroneous bookkeeping state can never self-heal because every call that would update it now fails on the same check first. This permanently blocks:
- `Deposit` (LPs cannot add liquidity),
- `Withdraw` (LPs cannot redeem LP tokens for underlying tokens — funds become permanently frozen in the pool),
- `WithdrawPnl` (protocol PnL owner cannot withdraw accrued PnL).

This satisfies "permanent freezing of user or LP funds" for the pool's liquidity providers.

### Likelihood Explanation
The check only fails when accumulated rounding pushes tracked last_k above real current_k; ordinary swap fee accrual normally grows k over time and masks small rounding drift, so this requires many `Deposit`/`Withdraw` cycles (attacker- or organically-driven) on a pool with small enough decimals/liquidity for the rounding error to be a non-negligible fraction of the total. This makes the bug more likely on low-liquidity or low-decimal pools, and is fully reachable via ordinary `Deposit`/`Withdraw` instructions available to any unprivileged LP with attacker-chosen amounts, requiring no special privileges.

### Recommendation
Recompute `target_orders.calc_pnl_x`/`calc_pnl_y` from the resulting real vault balances after each `Deposit`/`Withdraw` (fresh `normalize_decimal_v2` of the post-operation vault balances) rather than incrementally adding/subtracting independently-rounded deltas from the pre-operation `x1`/`y1`. Alternatively, clamp the `calc_take_pnl` invariant check to tolerate rounding-induced drift (e.g., allow a bounded epsilon, or fall back to resetting `calc_pnl_x`/`calc_pnl_y` to the real current values instead of erroring) so a legitimate sequence of deposits/withdrawals can never permanently brick pool operations.

### Proof of Concept
Conceptually (not a literal exploit, since a full numeric trace requires simulating many `Deposit`/`Withdraw` calls with concrete decimals/liquidity):
1. Attacker/LP repeatedly calls `Withdraw` with amounts chosen so that `pc_amount`/`coin_amount` (floor-rounded proportional shares) systematically under-subtract the true proportional share from `x1`/`y1` when computing the new `calc_pnl_x`/`calc_pnl_y` (double floor rounding via `exchange_pool_to_token` then `normalize_decimal_v2`).
2. Each iteration leaves `target_orders.calc_pnl_x * calc_pnl_y` (last_k) slightly larger relative to the real vault-balance-derived current_k than it should be, because the real vault balances are recomputed fresh (single rounding) each call while the bookkeeping value inherits all prior rounding leaks.
3. After sufficient iterations, `pool_pc_amount * pool_coin_amount < calc_pc_amount * calc_coin_amount` in `calc_take_pnl`, causing `AmmError::CalcPnlError` on the very next `Deposit`, `Withdraw`, or `WithdrawPnl` call.
4. Because the failing call reverts before the bookkeeping state can be corrected, every subsequent call to these three instructions fails identically, permanently freezing the pool's liquidity.

### Citations

**File:** program/src/processor.rs (L190-192)
```rust
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

**File:** program/src/processor.rs (L1756-1761)
```rust
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1818-1828)
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
