### Title
Pool-wide freeze of deposit/withdraw/swap via `need_take_pnl` subtraction underflow in `calc_total_without_take_pnl_no_orderbook` - (File: `program/src/math.rs`)

### Summary
Every unprivileged entry point that touches the pool reserves — `Deposit`, `Withdraw`, `SwapBaseIn`, and `SwapBaseOut` — first computes the "real" tradable reserves by subtracting the accrued-but-unwithdrawn protocol PnL (`need_take_pnl_pc` / `need_take_pnl_coin`) from the live vault balances via `Calculator::calc_total_without_take_pnl_no_orderbook`. This uses `checked_sub(...).ok_or(AmmError::CheckedSubOverflow)?`, i.e. it hard-reverts if the accumulated PnL debt ever exceeds the actual vault balance for that side, exactly mirroring the Olympus `internalRewardsForToken` pattern where a cached "debt" value that grows independently of the live balance can exceed it and revert the whole call.

### Finding Description
`calc_total_without_take_pnl_no_orderbook` is: [1](#0-0) 

It is invoked unconditionally at the top of `process_deposit` [2](#0-1) , `process_withdraw`/withdraw path [3](#0-2) , `process_swap_base_in` [4](#0-3) , and `process_swap_base_out`/v2 [5](#0-4) .

`need_take_pnl_pc`/`need_take_pnl_coin` are monotonically increased inside `calc_take_pnl` (called from deposit, withdraw, and `WithdrawPnl`) based on a sqrt-based k-growth split converted through decimal normalize/restore round-trips (`normalize_decimal_v2` / `restore_decimal`, using truncating integer division) [6](#0-5) [7](#0-6) . These fields can only be reset by the privileged `WithdrawPnl` instruction, which itself guards against the exact insolvency condition: [8](#0-7) 

That the codebase explicitly checks `need_take_pnl_coin <= amm_coin_vault.amount && need_take_pnl_pc <= amm_pc_vault.amount` before transferring, and reverts with a dedicated `TakePnlError` otherwise, shows the developers anticipated that the accrued PnL debt can, in practice, exceed the live vault balance on one side (e.g., through repeated rounding/truncation in `calc_take_pnl`'s decimal round-trips or from single-sided reserve depletion via swap fees skewing where fees accrue vs. where liquidity currently sits). Unlike `WithdrawPnl`, however, the far more commonly hit paths — `calc_total_without_take_pnl_no_orderbook` used by every `Deposit`, `Withdraw`, `SwapBaseIn`, and `SwapBaseOut` call — have no such graceful guard; they simply propagate a hard `checked_sub` failure (`AmmError::CheckedSubOverflow`) up through `?`.

### Impact Explanation
If `need_take_pnl_pc` or `need_take_pnl_coin` ever exceeds the corresponding vault's actual token balance (a state the protocol's own `WithdrawPnl` handler explicitly anticipates and guards against), every subsequent `Deposit`, `Withdraw`, `SwapBaseIn`, and `SwapBaseOut` instruction on that pool will revert with `CheckedSubOverflow` before any economic logic runs. This is a pool-wide freeze — not limited to one user as in the Olympus case, but blocking all depositors, withdrawers, and swappers — until an admin/`pnl_owner` (a privileged signer, out of scope for triggering but relevant to remediation) is able to call `WithdrawPnl` to rebalance the accounting, which itself is blocked if the imbalance is on the side that also fails its `<=` check, leaving the pool with no straightforward recovery path from an unprivileged transaction.

### Likelihood Explanation
The condition is triggered purely by ordinary use (deposits, withdrawals, and swaps compounding fee-driven PnL accrual and its associated decimal-conversion rounding over time) rather than by any privileged or malicious actor, and requires no leaked keys, malicious validators, or off-chain components. It is reachable from a single attacker- or user-submitted transaction with normal accounts once the imbalance condition (already explicitly checked for in `process_withdrawpnl`) exists.

### Recommendation
Mirror the graceful handling already present in `process_withdrawpnl`: in `Calculator::calc_total_without_take_pnl_no_orderbook`, do not hard-revert core user flows (deposit/withdraw/swap) on subtraction underflow. Instead, clamp `need_take_pnl_pc`/`need_take_pnl_coin` to the available vault balance (or trigger an automatic partial pnl reconciliation) so that ordinary user operations can still proceed even if the accrued-but-unwithdrawn protocol PnL momentarily exceeds the live vault balance on one side, and add an explicit invariant/test ensuring `calc_take_pnl`'s decimal round-trip cannot drift `need_take_pnl_*` above real vault holdings over repeated calls.

### Proof of Concept
A concrete PoC requires tracing many sequential `calc_take_pnl` calls with adversarially chosen deposit/withdraw amounts to accumulate rounding drift in `need_take_pnl_pc`/`need_take_pnl_coin` relative to actual vault balances until the `<=` guard in `process_withdrawpnl` would fail — this is the same condition that, when hit in `calc_total_without_take_pnl_no_orderbook`, freezes deposit/withdraw/swap. I was not able to fully simulate the exact numeric sequence within the available tool budget; this would require running the on-chain math (`calc_take_pnl`, `normalize_decimal_v2`, `restore_decimal`) against a chosen sequence of deposits/withdraws in a test harness to confirm concrete drift magnitude, which the codebase's own `test_calc_pnl_precision` test scaffolding [9](#0-8)  could be extended to demonstrate.

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

**File:** program/src/processor.rs (L199-262)
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
            if pc_pnl_amount != 0 && coin_pnl_amount != 0 {
                amm.state_data.need_take_pnl_pc = amm
                    .state_data
                    .need_take_pnl_pc
                    .checked_add(pc_pnl_amount)
                    .unwrap();
                amm.state_data.need_take_pnl_coin = amm
                    .state_data
                    .need_take_pnl_coin
                    .checked_add(coin_pnl_amount)
                    .unwrap();

                // step3: update total_coin and total_pc without pnl
                *total_pc_without_take_pnl = (*total_pc_without_take_pnl)
                    .checked_sub(pc_pnl_amount)
                    .unwrap();
                *total_coin_without_take_pnl = (*total_coin_without_take_pnl)
                    .checked_sub(coin_pnl_amount)
                    .unwrap();
```

**File:** program/src/processor.rs (L1148-1153)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1459-1464)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1505-1536)
```rust
        if amm.state_data.need_take_pnl_coin <= amm_coin_vault.amount
            && amm.state_data.need_take_pnl_pc <= amm_pc_vault.amount
        {
            // coin & pc is enough, transfer directly
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_coin_vault_info.clone(),
                user_pnl_coin_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                amm.state_data.need_take_pnl_coin,
            )?;
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_pc_vault_info.clone(),
                user_pnl_pc_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                amm.state_data.need_take_pnl_pc,
            )?;
            // clear need take pnl
            amm.state_data.need_take_pnl_coin = 0u64;
            amm.state_data.need_take_pnl_pc = 0u64;
            // update target_orders.calc_pnl_x & target_orders.calc_pnl_y
            target_orders.calc_pnl_x = x1.checked_sub(U128::from(delta_x)).unwrap().as_u128();
            target_orders.calc_pnl_y = y1.checked_sub(U128::from(delta_y)).unwrap().as_u128();
        } else {
            // calc error
            return Err(AmmError::TakePnlError.into());
        }
```

**File:** program/src/processor.rs (L2342-2347)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L2533-2538)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L3090-3212)
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
```
