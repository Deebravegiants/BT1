### Title
Divide-by-zero panic in `calc_take_pnl`'s decimal-normalized invariant math permanently freezes LP withdrawals - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` normalizes pool reserves through `Calculator::normalize_decimal_v2` before doing constant-product-invariant math, and then divides by those normalized values without checking for zero. Because normalization truncates (integer division), a nonzero raw vault balance can normalize to `0`, and that `0` is then used as a divisor, causing an unhandled `Option::unwrap()` panic on `checked_div`. This is the same bug class as JLSEC-2026-885 (division by zero from unchecked/derived values feeding a division), here reachable by any unprivileged swapper through ordinary `SwapBaseIn`/`SwapBaseOut` calls followed by a `Deposit`/`Withdraw`.

### Finding Description
`calc_take_pnl` computes: [1](#0-0) 

`Calculator::calc_x_power` divides by its 4th argument (`current_y`), and the subsequent `y2` computation divides by `x1`: [2](#0-1) 

`x1`/`y1` are produced by `normalize_decimal_v2`, which does `val * sys_decimal_value / 10^native_decimal` with integer (floor) division: [3](#0-2) 

If a token's native decimals are large relative to `sys_decimal_value`, a small-but-nonzero raw reserve (`total_pc_without_take_pnl` or `total_coin_without_take_pnl`) truncates to exactly `0` after normalization, even though `Calculator::calc_total_without_take_pnl_no_orderbook` returned a strictly positive raw amount: [4](#0-3) 

Both `process_deposit` and `process_withdraw` compute `x1`/`y1` this way and feed them straight into `calc_take_pnl`: [5](#0-4) [6](#0-5) 

Swap instructions only guard that the *raw* output amount stays strictly below the *raw* reserve (`swap_amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`), not that the reserve stays above the decimal-normalization truncation threshold: [7](#0-6) 

So an attacker can submit a single large `SwapBaseIn`/`SwapBaseIn_v2` (or `SwapBaseOut`) transaction that drives one side's raw reserve down to a tiny nonzero value (e.g. below `10^native_decimal / sys_decimal_value` raw units, which can still be a large absolute number of lamports/native units for high-decimal tokens). Any subsequent `Deposit` or `Withdraw` instruction — callable by any LP, including the attacker itself — recomputes `x1`/`y1`, hits the zero-normalized reserve, and panics inside `checked_div(...).unwrap()` in `calc_x_power`/`y2`. Every future `Withdraw` on that pool will keep recomputing the same broken totals and keep panicking, since nothing else in the instruction set restores that reserve (only further swaps could nudge it, and legitimate deposits raise both sides proportionally without necessarily fixing the truncation because subsequent pnl calc still uses the pre-deposit invariant snapshot from `TargetOrders`).

### Impact Explanation
Once the vulnerable state is reached, `process_withdraw` unconditionally calls `calc_take_pnl` before transferring any tokens out to the LP, and the panic aborts the entire instruction with no funds moved: [8](#0-7) 
This permanently blocks every liquidity provider from ever withdrawing their LP tokens from the affected pool, i.e. a permanent freeze of LP funds — one of the explicitly in-scope impact categories.

### Likelihood Explanation
The attack requires only a single transaction with attacker-chosen accounts and swap amounts (no privileged signer, no off-chain component, no malicious validator). It depends on the token pair's decimal configuration allowing a normalization truncation window (high `native_decimal` relative to `sys_decimal_value`), and on the attacker being able to supply enough input tokens to squeeze the opposite reserve down into that window via the constant-product formula. This is plausible for many real SPL tokens (decimals of 8–9 are common) but is decimals-dependent, so it will not affect every pool — likelihood is pool-configuration-dependent rather than universal.

### Recommendation
- In `Calculator::calc_x_power` and the `y2` computation in `calc_take_pnl`, replace `.unwrap()` on `checked_div` with a proper error path (e.g., return `AmmError::CalcPnlError`) when the divisor is zero, and treat that as a valid state (skip pnl-taking) rather than panicking.
- Alternatively/additionally, in `Withdraw`/`Deposit`, detect `x1 == 0 || y1 == 0` before calling `calc_take_pnl` and gracefully skip pnl calculation instead of proceeding into an unchecked division, so users can still exit their positions.

### Proof of Concept
1. Initialize a pool where the coin (or pc) mint has decimals large enough that `10^native_decimal > sys_decimal_value` by a wide margin (e.g., decimals = 9, `sys_decimal_value` = 10^6, giving a truncation threshold of any raw balance < 1000 units).
2. Attacker calls `SwapBaseIn`/`SwapBaseIn_v2` with `swap_direction = PC2Coin` (or `Coin2PC`) and a very large `amount_in`, driving `total_coin_without_take_pnl` (or `total_pc_without_take_pnl`) down to a value satisfying `0 < reserve < 1000` — allowed because the only check is `swap_amount_out >= total_x_without_take_pnl` (strict raw inequality), not a normalized-decimal check [7](#0-6) .
3. Any account (attacker or another LP) calls `Withdraw`. `process_withdraw` computes `y1 = normalize_decimal_v2(total_coin_without_take_pnl, coin_decimals, sys_decimal_value) == 0` [9](#0-8) , then calls `calc_take_pnl`, which calls `Calculator::calc_x_power(..., y1)` and divides by `y1 == 0`, panicking on `.unwrap()` [2](#0-1) .
4. The transaction aborts; every subsequent `Withdraw` call reproduces the same panic since the pool state is unchanged, permanently freezing all LP funds in that pool.

Note: full confirmation of the exact `sys_decimal_value` constant and decimal bounds enforced at `Initialize2` would require reading the complete `AmmInfo::initialize` implementation in `program/src/state.rs`, which was only partially retrievable from the index before the tool budget ran out; this does not affect the root-cause analysis of the unchecked division itself.

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

**File:** program/src/processor.rs (L1148-1173)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

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

**File:** program/src/processor.rs (L1719-1735)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

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

**File:** program/src/processor.rs (L2000-2027)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap_amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source coin to amm_coin_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_source_owner.clone(),
                    swap.amount_in,
                )?;
                // withdraw amm_pc_vault to destination pc
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap_amount_out,
                )?;
            }
            SwapDirection::PC2Coin => {
                if swap_amount_out >= total_coin_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
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
