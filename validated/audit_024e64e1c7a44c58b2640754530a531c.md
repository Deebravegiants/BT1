No vulnerability found for this question.

Raydium AMM's swap and pricing logic derives all amounts directly from live SPL token vault balances at transaction execution time via `Processor::unpack_token_account` and `Calculator::calc_total_without_take_pnl_no_orderbook`, then computes swap output with `Calculator::swap_token_amount_base_in`/`swap_token_amount_base_out` using the constant-product formula. [1](#0-0) [2](#0-1) 

There is no `AggregatorV3Interface`-style external price oracle, `latestRoundData()` call, or any cached/staleness-prone price feed anywhere in the in-scope swap/deposit/withdraw/initialize paths, PDA checks, `AmmInfo`/`AmmConfig`/`TargetOrders` loading, or SPL token CPIs. [3](#0-2)  The pnl/take-pnl accounting (`calc_take_pnl`) also computes price purely from the current pool reserves at call time, not from any external or delayed data source. [4](#0-3) 

Since the reachable surfaces (swap instructions, deposit/withdraw, initialize2) never consume a stale external oracle reading — all pricing is computed atomically from on-chain vault balances read within the same transaction — the "stale oracle price" bug class from the Chainlink-based report has no analog in this codebase.

### Citations

**File:** program/src/processor.rs (L159-190)
```rust
    /// The Detailed calculation of pnl
    /// 1. calc last_k witch dose not take pnl: last_k = calc_pnl_x * calc_pnl_y;
    /// 2. calc current price: current_price = current_x / current_y;
    /// 3. calc x after take pnl: x_after_take_pnl = sqrt(last_k * current_price);
    /// 4. calc y after take pnl: y_after_take_pnl = x_after_take_pnl / current_price;
    ///                           y_after_take_pnl = x_after_take_pnl * current_y / current_x;
    /// 5. calc pnl_x & pnl_y:  pnl_x = current_x - x_after_take_pnl;
    ///                         pnl_y = current_y - y_after_take_pnl;
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
```

**File:** program/src/processor.rs (L2321-2347)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;

        let user_source = Self::unpack_token_account(&user_source_info, spl_token_program_id)?;
        let user_destination =
            Self::unpack_token_account(&user_destination_info, spl_token_program_id)?;

        if !AmmStatus::from_u64(amm.status).swap_permission() {
            msg!(&format!("swap_base_in_v2: status {}", identity(amm.status)));
            return Err(AmmError::InvalidStatus.into());
        } else if amm.status == AmmStatus::WaitingTrade.into_u64() {
            let clock = Clock::get()?;
            if (clock.unix_timestamp as u64) < amm.state_data.pool_open_time {
                return Err(AmmError::InvalidStatus.into());
            } else {
                amm.status = AmmStatus::SwapOnly.into_u64();
                msg!("swap_base_in_v2: WaitingTrade to SwapOnly");
            }
        }

        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/math.rs (L80-104)
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
```

**File:** program/src/math.rs (L289-325)
```rust
    pub fn swap_token_amount_base_in(
        amount_in: U128,
        total_pc_without_take_pnl: U128,
        total_coin_without_take_pnl: U128,
        swap_direction: SwapDirection,
    ) -> U128 {
        let amount_out;
        match swap_direction {
            SwapDirection::Coin2PC => {
                // (x + delta_x) * (y + delta_y) = x * y
                // (coin + amount_in) * (pc - amount_out) = coin * pc
                // => amount_out = pc - coin * pc / (coin + amount_in)
                // => amount_out = ((pc * coin + pc * amount_in) - coin * pc) / (coin + amount_in)
                // => amount_out =  pc * amount_in / (coin + amount_in)
                let denominator = total_coin_without_take_pnl.checked_add(amount_in).unwrap();
                amount_out = total_pc_without_take_pnl
                    .checked_mul(amount_in)
                    .unwrap()
                    .checked_div(denominator)
                    .unwrap();
            }
            SwapDirection::PC2Coin => {
                // (x + delta_x) * (y + delta_y) = x * y
                // (pc + amount_in) * (coin - amount_out) = coin * pc
                // => amount_out = coin - coin * pc / (pc + amount_in)
                // => amount_out = (coin * pc + coin * amount_in - coin * pc) / (pc + amount_in)
                // => amount_out = coin * amount_in / (pc + amount_in)
                let denominator = total_pc_without_take_pnl.checked_add(amount_in).unwrap();
                amount_out = total_coin_without_take_pnl
                    .checked_mul(amount_in)
                    .unwrap()
                    .checked_div(denominator)
                    .unwrap();
            }
        }
        return amount_out;
    }
```
