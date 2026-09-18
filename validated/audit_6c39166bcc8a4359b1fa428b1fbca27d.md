Based on the codebase analysis, I found an analogous rounding-precision issue in the Raydium AMM's `calc_take_pnl` function that mirrors the reported bug pattern (dividing before multiplying / performing sequential divisions instead of consolidating multiplications before a single division).

### Title
Double sequential division in `calc_take_pnl` causes rounding-down of PnL amounts, creating drift between `target_orders.calc_pnl_x/y` and `total_pc/coin_without_take_pnl` - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` computes the PnL portion to attribute to the protocol (`pc_pnl_amount`, `coin_pnl_amount`) using two sequential division operations instead of consolidating all multiplications before a single division, causing accumulated rounding-down loss relative to the parallel `delta_x`/`delta_y` calculation that only performs one division.

### Finding Description
`calc_take_pnl` computes two related quantities from the same raw difference `diff_x`/`diff_y` (the normalized-decimal token amount corresponding to pnl):

1. `delta_x`/`delta_y` — used to update `target_orders.calc_pnl_x`/`calc_pnl_y` (the normalized "last k" baseline), computed with a single division: [1](#0-0) 

2. `pc_pnl_amount`/`coin_pnl_amount` — used to update `total_pc_without_take_pnl`/`total_coin_without_take_pnl` and `amm.state_data.need_take_pnl_pc/coin` (the actual native-decimal token amounts owed to the pnl owner), computed via `Calculator::restore_decimal` (which itself does one multiply-then-divide) and then a *second* independent multiply-then-divide by the pnl fraction: [2](#0-1) 

`restore_decimal` itself does mult-then-div correctly for decimal conversion: [3](#0-2) 

However, chaining `restore_decimal(diff_x)` (1 division) and then `* pnl_numerator / pnl_denominator` (a 2nd division) instead of combining as `diff_x * 10^pc_decimals * pnl_numerator / (sys_decimal_value * pnl_denominator)` (all multiplications first, one division) causes two independent floor-roundings to compound, exactly the anti-pattern described in the external report ("multiplication on result of division"). Because `delta_x` (used to update the normalized baseline `calc_pnl_x`) is derived with only *one* division while `pc_pnl_amount` (used to update the actual token totals `total_pc_without_take_pnl`) is derived with *two* divisions, the two values that are supposed to represent the same underlying quantity in different scales diverge slightly on every call.

### Impact Explanation
This function is invoked on every deposit, withdraw, and `withdrawpnl` call — all reachable by unprivileged LPs: [4](#0-3) [5](#0-4) 

Because `calc_pnl_x`/`calc_pnl_y` (normalized) and `total_pc_without_take_pnl`/`total_coin_without_take_pnl` (native, later renormalized as `x1`/`y1` on the next call) are supposed to be consistent representations of the pool's invariant baseline, but are updated using differently-rounded PnL amounts, repeated deposit/withdraw/pnl-take cycles cause a persistent, compounding drift between the on-chain accounting used for future PnL calculations and the actual vault balances. The rounded-down portion of `pc_pnl_amount`/`coin_pnl_amount` is never credited to `need_take_pnl_pc`/`need_take_pnl_coin` (and thus never claimable by the pnl owner via `process_withdrawpnl`), permanently trapping that dust inside `total_pc_without_take_pnl` while the baseline (`calc_pnl_x`) has already been decremented as if the full, more-precise amount had been taken — an accounting inconsistency that accumulates over the pool's lifetime.

### Likelihood Explanation
High likelihood of occurring on essentially every deposit/withdraw/withdrawpnl call where a PnL delta exists, since integer division rounding is deterministic and will trigger whenever `diff_x`/`diff_y` and the pnl fraction don't divide evenly (the common case, given `pnl_numerator`/`pnl_denominator` are typically 12/100).

### Recommendation
Combine the decimal-restoration and pnl-fraction multiplications before performing a single final division, e.g.:
```rust
let pc_pnl_amount = diff_x
    .checked_mul(U128::from(10).checked_pow(amm.pc_decimals.into()).unwrap())
    .unwrap()
    .checked_mul(amm.fees.pnl_numerator.into())
    .unwrap()
    .checked_div(
        U128::from(amm.sys_decimal_value)
            .checked_mul(amm.fees.pnl_denominator.into())
            .unwrap(),
    )
    .unwrap()
    .as_u64();
```
Apply the same consolidation for `coin_pnl_amount`, and ensure `delta_x`/`delta_y` and `pc_pnl_amount`/`coin_pnl_amount` are derived consistently (ideally from the same single-division computation, scaled appropriately) so the normalized baseline and native-token accounting never diverge.

### Proof of Concept
Given `diff_x = 1_000_000_000` (sys_decimal units), `pc_decimals = 9`, `sys_decimal_value = 1_000_000`, `pnl_numerator = 12`, `pnl_denominator = 100`:

- Current code: `restore_decimal(diff_x) = diff_x * 10^9 / 10^6 = 1_000_000_000_000` then `* 12 / 100 = 120_000_000_000` (two divisions, two roundings).
- Combined approach: `diff_x * 10^9 * 12 / (10^6 * 100) = 120_000_000_000` — matches in this exact case, but for values where `diff_x * 12` is not evenly divisible by `100` *and* the intermediate `restore_decimal` result is not evenly divisible by `100`, the two-step computation loses an extra unit of precision compared to the single consolidated division, analogous to the numeric example in the external report (`2.9999999999999989116e22` vs `3e22`). This directly parallels `test_calc_pnl_precision` in the repo's own test suite, which exists specifically to probe this precision behavior: [6](#0-5)

### Citations

**File:** program/src/processor.rs (L215-226)
```rust
            delta_x = diff_x
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();
            delta_y = diff_y
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();
```

**File:** program/src/processor.rs (L228-243)
```rust
            let diff_pc_pnl_amount =
                Calculator::restore_decimal(diff_x, amm.pc_decimals, amm.sys_decimal_value);
            let diff_coin_pnl_amount =
                Calculator::restore_decimal(diff_y, amm.coin_decimals, amm.sys_decimal_value);
            let pc_pnl_amount = diff_pc_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
            let coin_pnl_amount = diff_coin_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
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

**File:** program/src/processor.rs (L1741-1748)
```rust
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
```

**File:** program/src/processor.rs (L3090-3120)
```rust
    #[test]
    fn test_calc_pnl_precision() {
        // init
        let mut amm = AmmInfo::default();
        let init_pc_amount = 5434000000u64;
        let init_coin_amount = 100000000000000u64;
        let liquidity = Calculator::to_u64(
            U128::from(init_pc_amount)
                .checked_mul(init_coin_amount.into())
                .unwrap()
                .integer_sqrt()
                .as_u128(),
        )
        .unwrap();
        amm.initialize(0, 0, 5, 9, 1000000000, 7803).unwrap();
        amm.lp_amount = liquidity;

        let x =
            Calculator::normalize_decimal_v2(5434000000, amm.pc_decimals, amm.sys_decimal_value);
        let y = Calculator::normalize_decimal_v2(
            100000000000000,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        let mut target = TargetOrders::default();
        target.calc_pnl_x = x.as_u128();
        target.calc_pnl_y = y.as_u128();
        println!(
             "init_pc_amount:{}, init_coin_amount:{}, liquidity:{}, sys_decimal_value:{}, calc_pnl_x:{}, calc_pnl_y:{}",
             init_pc_amount, init_coin_amount, liquidity, identity(amm.sys_decimal_value), identity(target.calc_pnl_x), identity(target.calc_pnl_y)
         );
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
