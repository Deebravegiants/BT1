### Title
Unhandled division-by-zero panic in `calc_take_pnl` permanently bricks Deposit/Withdraw once pool reserves normalize to zero - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` normalizes pool reserves with `Calculator::normalize_decimal_v2` and then performs `checked_div(...).unwrap()` operations (via `Calculator::calc_x_power` and the `y2` computation) using the normalized reserves as divisors. Because `normalize_decimal_v2` floors dust-sized native token amounts to `0` when the token has a decimal count larger than `sys_decimal_value`'s exponent, an unprivileged LP can drive one side of the pool reserve into "dust" territory via the ordinary `Withdraw` instruction, causing `calc_take_pnl` to divide by a normalized `0` on the very next `Deposit` or `Withdraw` call. This triggers a Rust panic (`unwrap()` on `None`) instead of a graceful `AmmError`, and — because every subsequent call recomputes reserves from the same now-degenerate vault state — the pool becomes permanently unusable for `Deposit`/`Withdraw` by anyone.

### Finding Description
`calc_take_pnl` is invoked from both `process_deposit` and `process_withdraw` with `x1`/`y1` computed as: [1](#0-0) 
which calls: [2](#0-1) 

Inside `calc_take_pnl`, these normalized values are used as divisors without any zero-check: [3](#0-2) 
and `calc_x_power` itself divides unconditionally by `current_y`: [4](#0-3) 

If `x1` (normalized `total_pc_without_take_pnl`) or `y1` (normalized `total_coin_without_take_pnl`) is `0`, the `.checked_div(...).unwrap()` calls return `None` and `.unwrap()` panics, aborting the transaction with a low-level Rust panic rather than the intended `AmmError::CalcPnlError` path guarded elsewhere in the same function: [5](#0-4) 

An unprivileged LP fully controls the amount withdrawn via `Withdraw.amount` (bounded only by their own LP token balance), and `process_withdraw` allows withdrawing down to the point where remaining vault balances are dust: [6](#0-5) 
Because `normalize_decimal_v2` scales by `sys_decimal_value / 10^native_decimal`, any pool whose token decimals exceed `log10(sys_decimal_value)` will floor a small-but-nonzero native reserve to `0` once it's driven low enough. Since `total_pc_without_take_pnl`/`total_coin_without_take_pnl` are recomputed from live vault balances on every call, once the vault balance for either side is in this "dust" band, every future `Deposit` and `Withdraw` call on the pool will hit the same panic — a self-reinforcing, permanent denial of service.

### Impact Explanation
This is a direct structural analog to CVE-2017-3457 (an unprivileged/lower-effort actor causing a crash/hang of a stateful server process via a data-manipulation operation): here, a normal (non-privileged) LP action (`Withdraw`) can push shared, persistent on-chain pool state into a configuration that makes the core `Deposit`/`Withdraw` code paths panic for every subsequent caller. Because Solana account state persists across transactions and the panic condition is a function of the vault balances (not of who is calling), this permanently freezes all other LPs' ability to deposit or withdraw from the affected pool, i.e., a permanent freezing of LP funds.

### Likelihood Explanation
Reachable in a single transaction from the public `Withdraw` instruction with attacker-chosen `amount`, requiring only that the caller already holds (or acquires) enough LP tokens to withdraw the pool down into the dust band — this is a realistic, unprivileged, self-serve action available to any LP for pools using coin/pc mints with decimals large relative to `sys_decimal_value`.

### Recommendation
Replace the unchecked `.unwrap()` calls on `checked_div`/`checked_mul` in `Calculator::calc_x_power` and in `Processor::calc_take_pnl` (`y2` computation, and the `pc_pnl_amount`/`coin_pnl_amount` division chain) with proper error propagation (`ok_or(AmmError::CheckedDivOverflow)?`), and add an explicit guard rejecting/handling the case where normalized `x1`/`y1` (or their pre-normalization native reserves) are zero before entering the pnl-take branch, returning a typed `AmmError` instead of panicking.

### Proof of Concept
1. Create/target a pool where the pc or coin mint has decimals such that `10^decimals > sys_decimal_value` (e.g., decimals=9 with `sys_decimal_value = 10^6`, as used throughout `math.rs`'s own tests, e.g. `amm.initialize(0, 0, 2, 9, 1000000, 1)` in `program/src/processor.rs:3223`).
2. As an LP, repeatedly call `Withdraw` with `amount` values approaching the LP's full balance, driving the pc or coin vault balance down to a native amount that, once fed through `Calculator::normalize_decimal_v2` (`program/src/math.rs:106-116`), floors to `0`.
3. Submit one more `Withdraw` (or `Deposit`) call; `calc_take_pnl`'s `calc_x_power`/`y2` division (`program/src/processor.rs:199-209`, `program/src/math.rs:50-60`) divides by the now-zero normalized reserve, panics, and the transaction aborts.
4. Because the vault balances remain in this degenerate state after the failed transaction (state changes from a panicking instruction are not applied, but the *pre-existing* vault balances that caused the divide-by-zero persist), every future `Deposit`/`Withdraw` call against this pool will deterministically hit the same panic, permanently freezing LP funds in the pool.

### Citations

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

**File:** program/src/processor.rs (L267-278)
```rust
        } else {
            msg!(arrform!(
                LOG_SIZE,
                "calc_take_pnl error x:{}, y:{}, calc_pnl_x:{}, calc_pnl_y:{}",
                x1,
                y1,
                identity(target.calc_pnl_x),
                identity(target.calc_pnl_y)
            )
            .as_str());
            return Err(AmmError::CalcPnlError.into());
        }
```

**File:** program/src/processor.rs (L1155-1164)
```rust
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
```

**File:** program/src/processor.rs (L1751-1816)
```rust
        // coin_amount / total_coin_amount = amount / lp_mint.supply => coin_amount = total_coin_amount * amount / pool_mint.supply
        let invariant = InvariantPool {
            token_input: withdraw.amount,
            token_total: amm.lp_amount,
        };
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;

        encode_ray_log(WithdrawLog {
            log_type: LogType::Withdraw.into_u8(),
            withdraw_lp: withdraw.amount,
            user_lp: user_source_lp.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            pool_lp: amm.lp_amount,
            calc_pnl_x: target_orders.calc_pnl_x,
            calc_pnl_y: target_orders.calc_pnl_y,
            out_coin: coin_amount,
            out_pc: pc_amount,
        });
        if withdraw.amount == 0 || coin_amount == 0 || pc_amount == 0 {
            return Err(AmmError::InvalidInput.into());
        }

        if coin_amount < amm_coin_vault.amount && pc_amount < amm_pc_vault.amount {
            if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some() {
                if withdraw.min_coin_amount.unwrap() > coin_amount
                    || withdraw.min_pc_amount.unwrap() > pc_amount
                {
                    return Err(AmmError::ExceededSlippage.into());
                }
            }
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_coin_vault_info.clone(),
                user_dest_coin_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                coin_amount,
            )?;
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_pc_vault_info.clone(),
                user_dest_pc_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                pc_amount,
            )?;
            Invokers::token_burn(
                token_program_info.clone(),
                user_source_lp_info.clone(),
                amm_lp_mint_info.clone(),
                source_lp_owner_info.clone(),
                withdraw.amount,
            )?;
            amm.lp_amount = amm.lp_amount.checked_sub(withdraw.amount).unwrap();
        } else {
            // calc error
            return Err(AmmError::TakePnlError.into());
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
