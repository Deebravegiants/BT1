## Finding

### Title
Uncaught panic in AMM PnL calculation via unchecked triple-multiplication overflow in `calc_x_power` - (File: `program/src/math.rs`)

### Summary
`Calculator::calc_x_power` performs a chained three-term `U256` multiplication (`last_x * last_y * current_x`) using `.checked_mul(...).unwrap()` instead of returning a graceful error on overflow. Because the normalized token amounts (`x1`/`y1`) that feed this function are derived from `normalize_decimal_v2`, whose magnitude scales with `sys_decimal_value = 10^max(pc_decimals, coin_decimals)`, a pool created with an asymmetric/high-decimal token pair can push the product of these normalized values past the `U256` capacity (`2^256`), causing the `unwrap()` to panic instead of returning an `AmmError`. This mirrors the ORML `add_share` bug class: unvalidated user-influenced magnitude reaches raw arithmetic before any bounds check, and the overflow manifests as an uncaught Rust panic rather than a checked error.

### Finding Description
`sys_decimal_value` is set in `AmmInfo::initialize` (called from `process_initialize2`, reachable by any unprivileged pool creator) as `10^max(pc_decimals, coin_decimals)` using the *actual mint decimals* of the two tokens supplied to `Initialize2`: [1](#0-0) 

Since the pool creator fully controls which SPL mints are used (and can mint themselves an arbitrary custom token with `decimals = 0` alongside another mint with `decimals` up to 19, the largest value for which `checked_pow` does not itself panic during `initialize`), they can force `sys_decimal_value` up to `10^19`.

`normalize_decimal_v2` scales a raw `u64` vault amount by `sys_decimal_value` and divides by `10^native_decimal`: [2](#0-1) 

When `native_decimal` (e.g. `coin_decimals = 0`) is much smaller than `sys_decimal_value`'s exponent, the normalized value (`y1`/`target.calc_pnl_y`) can approach `2^127`, i.e. near the top of `u128` range, while raw vault balances are still valid `u64` amounts.

These normalized, persisted values (`target.calc_pnl_x` / `target.calc_pnl_y`) and the freshly computed `x1`/`y1` are then fed into `calc_x_power`, which multiplies three such large values together as `U256` with an unconditional `.unwrap()`: [3](#0-2) 

`calc_x_power` is invoked from `Processor::calc_take_pnl`: [4](#0-3) 

`calc_take_pnl` is called from `process_deposit`, `process_withdraw`, and `process_withdrawpnl` — all reachable by ordinary LPs/pool participants with attacker-chosen accounts/data: [5](#0-4) 

With `last_x`, `last_y`, and `current_x` each approaching magnitudes on the order of `2^64`–`2^127` (achievable by choosing an extreme-decimal token pair and large but valid `u64` balances), the product `last_x * last_y * current_x` can exceed `2^256`, causing `checked_mul` to return `None` and the subsequent `.unwrap()` to panic.

### Impact Explanation
Once a pool is initialized with such a decimal/amount combination, every subsequent `Deposit`, `Withdraw`, and `WithdrawPnl` instruction that reaches `calc_take_pnl` will panic and abort. `Withdraw` has a conditional bypass only when `amm.status == AmmStatus::WithdrawOnly` (an owner-only/privileged state transition via `SetParams`), so ordinary LPs cannot self-rescue funds; `Deposit` and `WithdrawPnl` have no such bypass. This results in the pool's liquidity becoming unusable/frozen for normal LP operations without privileged administrator intervention — an availability/fund-freezing impact consistent with the "permanent freezing of user or LP funds" acceptance criterion.

### Likelihood Explanation
Exploitability depends on an attacker creating a pool (`Initialize2`, an unprivileged, in-scope instruction) using a custom SPL mint with an extreme decimals value (e.g. `0`) paired with another mint using close to the maximum decimals that `sys_decimal_value`'s `checked_pow` will tolerate (up to `19`), combined with large (but individually valid `u64`) vault balances that the attacker controls (since they mint their own token supply). This is fully achievable by a single unprivileged actor using one transaction to create the pool and normal LP transactions afterward — no privileged signer or off-chain component is required.

### Recommendation
Replace the `.unwrap()` calls in `Calculator::calc_x_power` (and the surrounding `checked_mul`/`checked_sub` chains in `calc_take_pnl`) with proper error propagation (`ok_or(AmmError::...)?`), and/or bound `sys_decimal_value`/decimal deltas at `Initialize2` time to prevent normalized magnitudes from approaching `U256` overflow thresholds in the PnL calculation.

### Proof of Concept
1. Attacker mints a custom SPL token A with `decimals = 0` and mints themselves a large raw supply (up to `u64::MAX`).
2. Attacker pairs token A with a second mint B having `decimals` close to `19` (the largest value `AmmInfo::initialize`'s `checked_pow(10, decimals)` can compute without itself panicking).
3. Attacker calls `Initialize2` (`program/src/processor.rs:process_initialize2`) with large `init_pc_amount`/`init_coin_amount` for these mints, establishing `sys_decimal_value = 10^19` and correspondingly large normalized `target.calc_pnl_x`/`calc_pnl_y` values.
4. Attacker (or any LP) then calls `Deposit`, `Withdraw`, or `WithdrawPnl` on this pool; `calc_take_pnl` → `calc_x_power` computes `last_x.checked_mul(last_y).unwrap().checked_mul(current_x).unwrap()...`, which overflows `U256` and panics, aborting the transaction and leaving the pool's LP funds unable to be withdrawn or deposited into through normal instructions.

### Citations

**File:** program/src/state.rs (L737-745)
```rust
        if pc_decimals > coin_decimals {
            self.sys_decimal_value = (10 as u64)
                .checked_pow(pc_decimals.try_into().unwrap())
                .unwrap();
        } else {
            self.sys_decimal_value = (10 as u64)
                .checked_pow(coin_decimals.try_into().unwrap())
                .unwrap();
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

**File:** program/src/processor.rs (L1741-1749)
```rust
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
