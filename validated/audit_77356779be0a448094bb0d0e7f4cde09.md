### Title
Panic-based Denial of Service via unguarded `checked_sub().unwrap()` in `calc_take_pnl` — permanent freeze of Deposit/Withdraw/WithdrawPnl for a pool - ([File: program/src/processor.rs])

### Summary
`Processor::calc_take_pnl` performs `x1.checked_sub(x2).unwrap()` / `y1.checked_sub(y2).unwrap()` on the pool's normalized token balances, where `x2`/`y2` are derived from an `integer_sqrt()` of a value computed with intermediate rounding (`calc_x_power`, `restore_decimal`, `normalize_decimal_v2`). If rounding causes `x2 > x1` (or `y2 > y1`) the subtraction underflows and the transaction panics instead of returning a handled `AmmError`, unlike every other subtraction on this exact code path (e.g. `checked_total_without_take_pnl`, `exchange_pool_to_token`), which are guarded with `.ok_or(...)`.

### Finding Description
`calc_take_pnl` is invoked from `process_deposit`, `process_withdraw`, and `process_withdraw_pnl` — all instructions reachable by an ordinary unprivileged LP/user in a single transaction, after only routine account/signer/status validation, with no special privilege required. [1](#0-0) 

Inside the function, the "pnl accrued" branch computes `x2`/`y2` from an on-chain stored `TargetOrders.calc_pnl_x/calc_pnl_y` baseline and the pool's live vault balances, then subtracts:
```
let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
``` [2](#0-1) 

`x2` is derived via `integer_sqrt()` of `calc_x_power(...)`, and `y2` via `x2 * y1 / x1` — both involve integer division/rounding. [3](#0-2) 

Every other numeric conversion feeding into `x1`/`y1`/`calc_pnl_x`/`calc_pnl_y` (`normalize_decimal_v2`, `restore_decimal`) itself uses unguarded `.unwrap()` on `checked_mul`/`checked_div`, so precision loss is baked into the pipeline (mirrored exactly by the project's own `test_calc_pnl_precision` test, which exists specifically to explore precision edge cases around this function). [4](#0-3) [5](#0-4) 

Contrast this with the sibling function `calc_total_without_take_pnl_no_orderbook`, which subtracts related pool quantities and explicitly returns `AmmError::CheckedSubOverflow` instead of panicking: [6](#0-5) 

Because `calc_pnl_x`/`calc_pnl_y` are persisted in the `TargetOrders` account (on-chain state, not per-transaction), if a sequence of trades/deposits/withdrawals drives the stored baseline and live vault ratio into a state where `x2 > x1` or `y2 > y1` is computed, **every subsequent call to Deposit, Withdraw, and WithdrawPnl on that pool will deterministically panic** at the same `.unwrap()`, since the stored state that triggers the underflow is not rolled back or correctable by any of the callable instructions in scope. This is the direct analog of the CVE's NULL pointer dereference: an unguarded panic condition reachable pre-privilege by any account, differing only in that the underlying primitive is an arithmetic `unwrap()` panic (Rust's crash-equivalent) rather than a literal null-pointer read, per the report's "bug-class hint" framing.

### Impact Explanation
A successful trigger does not merely fail one transaction — because the offending values live in persistent on-chain `TargetOrders` state, the panic condition is reproduced on every future call to `process_deposit`, `process_withdraw`, and `process_withdraw_pnl` for that pool. That permanently freezes all LP deposit/withdrawal and PnL-owner withdrawal functionality for the affected pool, i.e. locking user and LP funds in the vaults with no path in the current instruction set to reset `TargetOrders.calc_pnl_x/calc_pnl_y` back to a safe state. This satisfies "permanent freezing of user or LP funds."

### Likelihood Explanation
Reaching the vulnerable branch requires the pool's current `pool_pc * pool_coin >= calc_pc_amount * calc_coin_amount` gate to pass (line 190-192) and then an accumulation of rounding error across many normalize/restore/sqrt operations to produce `x2 > x1` or `y2 > y1`. This is a rounding-edge-case rather than a directly attacker-forced one-shot bug: it likely requires a specific, crafted sequence of swaps/deposits/withdrawals (all of which are unprivileged, attacker-composable instructions) to nudge the stored baseline versus live-vault ratio into the underflow region. I could not fully enumerate concrete numeric inputs that trigger it within the scope of this review, so likelihood should be treated as **Medium** rather than confirmed-high, pending off-chain arithmetic simulation of `calc_x_power`/`integer_sqrt` under adversarial trade sequences.

### Recommendation
Replace the four unguarded `.unwrap()` calls in `calc_take_pnl` (`x1.checked_sub(x2).unwrap()`, `y1.checked_sub(y2).unwrap()`, and the analogous `checked_sub` calls on `target_orders.calc_pnl_x/calc_pnl_y` in `process_deposit`/`process_withdraw`/`process_withdraw_pnl`) with `.ok_or(AmmError::CalcPnlError)?` (or equivalent), mirroring the pattern already used in `calc_total_without_take_pnl_no_orderbook`. Additionally consider saturating (`saturating_sub`) or clamping `x2`/`y2` to `x1`/`y1` when rounding would otherwise cause underflow, since the sqrt-based approximation is expected to be extremely close but not exact.

### Proof of Concept
Exact numeric inputs that drive `x2 > x1` were not derived within this review — this would require iterating `calc_x_power`/`integer_sqrt` over a wide range of pool ratios/decimals combinations (as hinted at by the project's own `test_calc_pnl_precision` unit test, which was written to probe this exact rounding surface but does not assert against underflow). The existing test: [5](#0-4) 
demonstrates the reachable call sequence (`initialize` → deposit-equivalent state → `calc_take_pnl` → withdraw → `calc_take_pnl` again) that would need to be fuzzed with extreme decimal-precision mismatches (`pc_decimals` vs `coin_decimals`) and large swap volumes to find a concrete underflow-triggering input set.

### Citations

**File:** program/src/processor.rs (L167-220)
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
            delta_x = diff_x
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();
```

**File:** program/src/processor.rs (L3090-3213)
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

        // withdraw
        let withdraw_lp = 2577470628u64;
        let mut total_pc_without_take_pnl = init_pc_amount;
        let mut total_coin_without_take_pnl = init_coin_amount;
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

        let (delta_x, delta_y) = Processor::calc_take_pnl(
            &target,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )
        .unwrap();
        println!("delta_x:{}, delta_y:{}", delta_x, delta_y);
        // coin_amount / total_coin_amount = amount / lp_mint.supply => coin_amount = total_coin_amount * amount / pool_mint.supply
        let invariant = InvariantPool {
            token_input: withdraw_lp,
            token_total: amm.lp_amount,
        };
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)
            .unwrap();
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)
            .unwrap();

        amm.lp_amount = amm.lp_amount.checked_sub(withdraw_lp).unwrap();
        target.calc_pnl_x = x1
            .checked_sub(Calculator::normalize_decimal_v2(
                pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target.calc_pnl_y = y1
            .checked_sub(Calculator::normalize_decimal_v2(
                coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
        total_pc_without_take_pnl = total_pc_without_take_pnl.checked_sub(pc_amount).unwrap();
        total_coin_without_take_pnl = total_coin_without_take_pnl
            .checked_sub(coin_amount)
            .unwrap();
        println!(
             "withdraw calc_pnl_x:{}, calc_pnl_y:{}, total_pc_without_take_pnl:{}, total_coin_without_take_pnl:{}",
             identity(target.calc_pnl_x), identity(target.calc_pnl_y), total_pc_without_take_pnl, total_coin_without_take_pnl
         );

        // withdraw 2
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

        let (delta_x, delta_y) = Processor::calc_take_pnl(
            &target,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )
        .unwrap();
        println!("delta_x:{}, delta_y:{}", delta_x, delta_y);
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
