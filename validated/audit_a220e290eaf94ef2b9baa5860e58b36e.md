### Title
Rounding-Induced Spurious Failure in `calc_take_pnl` Product Check Can Permanently Freeze Deposits/Withdrawals - ([File: program/src/processor.rs])

### Summary
`Processor::calc_take_pnl` gates every `Deposit`, `Withdraw`, and `WithdrawPnl` instruction behind a strict inequality comparing the pool's raw vault-token product against a decimal-restored version of the AMM's internally-tracked "last taken" reference amounts (`target.calc_pnl_x` / `target.calc_pnl_y`). Because these reference amounts are stored in a normalized fixed-point representation (`sys_decimal_value`) and must be round-tripped through truncating integer division/multiplication to compare against raw vault balances, the comparison can fail even when no economic imbalance exists — mirroring the reported Bank::recall rounding-assertion bug class, except here the failure surfaces as a hard `Err(AmmError::CalcPnlError)` return that blocks the instruction rather than a Move `abort`.

### Finding Description
`calc_take_pnl` restores `target.calc_pnl_x`/`target.calc_pnl_y` (stored at `sys_decimal_value` precision) back to native-token precision via `Calculator::restore_decimal`, then requires: [1](#0-0) 

```
let calc_pc_amount = Calculator::restore_decimal(target.calc_pnl_x..., amm.pc_decimals, amm.sys_decimal_value);
let calc_coin_amount = Calculator::restore_decimal(target.calc_pnl_y..., amm.coin_decimals, amm.sys_decimal_value);
let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
    >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
{ ... } else {
    return Err(AmmError::CalcPnlError.into());
}
```

`target.calc_pnl_x`/`calc_pnl_y` are themselves produced by `Calculator::normalize_decimal_v2`, which performs a truncating (floor) integer division when scaling native-decimal vault amounts down to `sys_decimal_value`: [2](#0-1) 

and `restore_decimal` performs the inverse truncating operation: [3](#0-2) 

Because normalize→restore is a lossy round-trip (both directions floor), `restore_decimal(normalize_decimal_v2(v))` is not guaranteed to equal `v`; it can be strictly less. When a `Deposit` or `Withdraw` updates `calc_pnl_x`/`calc_pnl_y` from the *normalized* (`x1`/`y1`) values instead of directly from the raw vault totals, the subsequently restored `calc_pc_amount`/`calc_coin_amount` used in the next `calc_take_pnl` call can end up larger than the true current raw pool totals purely from truncation drift, especially compounded over repeated deposit/withdraw cycles and with tokens of differing decimals (`pc_decimals` vs `coin_decimals`, both distinct from `sys_decimal_value`). This flips the `>=` check to false and the instruction aborts with `AmmError::CalcPnlError`: [4](#0-3) [5](#0-4) 

`calc_take_pnl` is invoked from `process_deposit`, `process_withdraw`, and `process_withdrawpnl`: [6](#0-5) [7](#0-6) [8](#0-7) 

Since the on-chain state (`target_orders.calc_pnl_x/y` and vault balances) is only mutated when a transaction succeeds, a spurious `CalcPnlError` leaves the state unchanged; the *next* call recomputes with the identical inputs and fails identically. Because both `x1`/`y1` (from the current vault balances) and `target.calc_pnl_x/y` are deterministic functions of on-chain state, once this inequality flips false there is no permissionless way to make it true again — any attacker-chosen `Deposit`/`Withdraw` transaction that lands on a pool in this state will keep aborting, and `process_withdraw`'s normal (non `WithdrawOnly`) path always calls `calc_take_pnl`, so LPs cannot withdraw funds through the standard instruction.

### Impact Explanation
If the drift accumulates such that the check fails, `Deposit` and `Withdraw` (and `WithdrawPnl`) become permanently unusable for that pool: LPs cannot add or remove liquidity, and pending PnL cannot be swept. Because the underlying token balances are unaffected by the failed transactions, the funds remain locked in the AMM vaults with no permissionless recovery path — meeting the "permanent freezing of user or LP funds" bar. This is reachable from a single submitted `Deposit`/`Withdraw`/`WithdrawPnl` transaction with normal attacker-chosen amounts (no privileged signer needed), since any user's transaction, not just an attacker's, will trip the same deterministic check once the pool state drifts into the failing region.

### Likelihood Explanation
The drift is a function of `pc_decimals`, `coin_decimals`, `sys_decimal_value`, and pool amount magnitudes/ratios, and accumulates through repeated deposit/withdraw cycles. For AMM pairs where token decimals diverge substantially from `sys_decimal_value` (e.g. very small or very large native decimals relative to the sys value used for pnl accounting), or after many deposit/withdraw operations, the probability of the strict inequality flipping increases. This is not attacker-controlled to guarantee on-demand, but it is a pool-wide condition reachable through ordinary user activity (repeated deposits/withdrawals), matching the "frequent" nature described in the analogous report.

### Recommendation
Replace the strict `>=` product check in `calc_take_pnl` with a tolerance-based comparison (or use consistent non-lossy fixed-point representations end-to-end, e.g. store `calc_pnl_x/y` directly in native-token units instead of round-tripping through `sys_decimal_value`), so that rounding drift from `normalize_decimal_v2`/`restore_decimal` cannot cause `Deposit`/`Withdraw`/`WithdrawPnl` to permanently fail. At minimum, allow a small epsilon margin or clamp `calc_pc_amount`/`calc_coin_amount` to the actual pool totals when they exceed them due to rounding, rather than returning a hard error that can recur indefinitely for the same on-chain state.

### Proof of Concept
1. Create a pool where `pc_decimals`/`coin_decimals` differ significantly from `amm.sys_decimal_value` (e.g. `sys_decimal_value = 10^6`, `pc_decimals = 9`, `coin_decimals = 5`, as used in `test_calc_pnl_precision`).
2. Perform a sequence of `Deposit` and `Withdraw` operations with amounts chosen to maximize floor-truncation loss in `normalize_decimal_v2`/`restore_decimal` (e.g. amounts whose ratio to `sys_decimal_value` conversion leaves large remainders each time), each of which updates `target_orders.calc_pnl_x/y` from the normalized `x1`/`y1` at [4](#0-3)  or [5](#0-4) .
3. After enough cycles, submit another `Deposit`/`Withdraw`/`WithdrawPnl`; `calc_take_pnl`'s check at [9](#0-8)  evaluates false and the instruction returns `AmmError::CalcPnlError`, and every subsequent attempt with the same (unchanged) on-chain state fails identically, demonstrating the permanent block on deposits/withdrawals for that pool.

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

**File:** program/src/math.rs (L96-104)
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
