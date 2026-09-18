### Title
Decimal-precision mismatch between the pnl-take gating check and the actual `x1/y2` subtraction in `calc_take_pnl` can panic on unsigned underflow, DoSing Deposit/Withdraw/WithdrawPnl - (File: program/src/processor.rs)

### Summary
`Processor::calc_take_pnl` gates its pnl-taking branch with a comparison performed in *native* decimal units, but performs the actual `checked_sub().unwrap()` subtraction using values that are calculated in *normalized* (`sys_decimal_value`) units through a different rounding path. Because `normalize_decimal_v2`/`restore_decimal` are lossy integer-division round trips, the gating comparison can hold true while the underlying normalized quantities used for the subtraction are inverted, causing an unwrap-panic that reverts the transaction — a direct analog of the Zaros `Vault._updateCreditDelegations` underflow, where a delta between "new" and "previous" state was computed with an unsigned type whose ordering invariant was assumed but not actually guaranteed in every code path.

### Finding Description
In `calc_take_pnl` [1](#0-0) , the gating condition is:

```rust
let calc_pc_amount = Calculator::restore_decimal(target.calc_pnl_x.into(), amm.pc_decimals, amm.sys_decimal_value);
let calc_coin_amount = Calculator::restore_decimal(target.calc_pnl_y.into(), amm.coin_decimals, amm.sys_decimal_value);
let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
    >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
``` [2](#0-1) 

This check compares native-unit balances (`total_pc_without_take_pnl`, `total_coin_without_take_pnl`) against `target.calc_pnl_x`/`calc_pnl_y` after `restore_decimal` has converted them from stored normalized units back to native units.

Once the check passes, the code computes `x2`/`y2` and immediately subtracts using a *different* representation — `x1`, `y1` are the **normalized** versions of the same totals (produced by `normalize_decimal_v2` before the call), and they are combined directly with the raw, normalized `target.calc_pnl_x`/`calc_pnl_y` (no restore/renormalize round trip):

```rust
let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
``` [3](#0-2) 

`x1`, `y1`, and `x2` (via `calc_x_power`) are all computed in `sys_decimal_value` units [4](#0-3) , while the branch-gating comparison was performed in native `pc_decimals`/`coin_decimals` units. `normalize_decimal_v2`/`restore_decimal` truncate on integer division [5](#0-4) , so `restore_decimal(normalize_decimal_v2(v))` is not guaranteed to equal `v`, and the reverse round trip used for the gate (`restore_decimal(target.calc_pnl_x)` vs. raw pool amounts) does not use the exact same values fed into the subtraction (`x1` vs. `target.calc_pnl_x` directly). When `pc_decimals` and `coin_decimals` differ from `sys_decimal_value` and from each other (the normal Raydium configuration, e.g. USDC 6 decimals vs. SOL 9 decimals vs. an internal `sys_decimal_value`), rounding on one side of the inequality can diverge from rounding on the other side used inside `calc_x_power`, so the native-unit gate `pool_pc*pool_coin >= calc_pc*calc_coin` can be satisfied while the normalized quantity `x2` (which mathematically requires `last_k <= current_k` in *normalized* units to guarantee `x2 <= x1`) ends up greater than `x1`, flipping the subtraction and triggering the `unwrap()` panic.

This is directly analogous to the reported Zaros bug: an unsigned subtraction (`new - previous`) is performed on two values whose relative ordering is assumed from a separate, imprecisely-related check, and that assumption can silently break due to precision effects, causing every subsequent call to revert.

### Impact Explanation
`calc_take_pnl` is invoked from `process_deposit` [6](#0-5)  and `process_withdraw`/`WithdrawPnl` [7](#0-6) , both of which are reachable by any unprivileged user (any LP calling Deposit or Withdraw). If the described precision mismatch is hit for a given pool's `target_orders` state, the `.unwrap()` panics and the instruction reverts, meaning that particular pool's Deposit/Withdraw (and the take-pnl step embedded in it) becomes permanently unusable until `target_orders`/vault state changes enough to move the values back into the "safe" region — this can amount to a persistent DoS of core LP functionality for the affected pool, matching the reported bug class's "protocol DoS" impact.

### Likelihood Explanation
This requires accumulated rounding drift between `pc_decimals`, `coin_decimals`, and `sys_decimal_value` to reach the precise boundary condition where the native-unit gate and the normalized-unit subtraction disagree. This is more likely for pools with token pairs of very different decimal counts (e.g. a 2-decimal token paired with a 9-decimal token) and can be nudged closer to the boundary over many swaps/deposits/withdraws that each perturb `total_pc_without_take_pnl`/`total_coin_without_take_pnl` and `target.calc_pnl_x/y` by rounding remainders. It is not trivially triggerable in one transaction from a fresh pool, but is reachable through repeated normal LP/swap activity without any privileged action, making it a plausible medium-likelihood DoS vector rather than a guaranteed one.

### Recommendation
Perform the gating comparison using the same unit representation (and the same rounding path) that is used for the subsequent subtraction — i.e., compare `x1 * y1` against `target.calc_pnl_x * target.calc_pnl_y` directly in normalized units instead of restoring `target.calc_pnl_x/y` to native units and comparing against raw native balances. Alternatively, replace the `checked_sub().unwrap()` calls at lines 213–214 with saturating subtraction (clamping to zero) or an explicit `ok_or`-guarded error return, so a rounding-induced sign flip degrades gracefully instead of panicking and permanently DoSing the affected pool.

### Proof of Concept
Conceptual PoC (decimal-mismatch driven):
1. Create a pool where `pc_decimals` and `coin_decimals` differ significantly from `amm.sys_decimal_value` (e.g. pc_decimals = 2, coin_decimals = 9), matching realistic token configurations.
2. Perform a sequence of swaps and deposits so that `total_pc_without_take_pnl`/`total_coin_without_take_pnl` and `target_orders.calc_pnl_x/calc_pnl_y` accumulate independent rounding remainders from repeated `normalize_decimal_v2`/`restore_decimal` conversions (lines in `program/src/math.rs:80-116`, used throughout deposit/withdraw/swap flows).
3. Call `Deposit` or `Withdraw` at the point where `restore_decimal(target.calc_pnl_x)*restore_decimal(target.calc_pnl_y)` (native units) is ≤ `pool_pc_amount*pool_coin_amount`, satisfying the gate at `program/src/processor.rs:190-192`, while the normalized `target.calc_pnl_x*target.calc_pnl_y` (used inside `calc_x_power`) is actually greater than `x1*y1`.
4. `calc_x_power` produces `x2 > x1` (or `y2 > y1`), and the `checked_sub().unwrap()` at `program/src/processor.rs:213-214` panics, reverting the Deposit/Withdraw instruction and DoSing that call path for the pool.

### Citations

**File:** program/src/processor.rs (L167-192)
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
```

**File:** program/src/processor.rs (L211-214)
```rust
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
