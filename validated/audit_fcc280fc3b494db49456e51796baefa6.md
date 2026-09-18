### Title
Division-by-zero panic in `swap_token_amount_base_out` when `amount_out` equals the pool's total available balance on the output side - (File: `program/src/math.rs`, `program/src/processor.rs`)

### Summary
`Calculator::swap_token_amount_base_out` computes the required input amount for a base-out swap by dividing by `(total_output_without_take_pnl - amount_out)`. This subtraction is not guaranteed to be nonzero before the division happens, because the check that rejects `amount_out >= total_output_without_take_pnl` is performed **after** the division in both `process_swap_base_out` and `process_swap_base_out_v2`. A caller who submits `amount_out` exactly equal to the current total (un-taken-pnl) balance of the output token causes a division by zero, which panics the transaction (denial of service), analogous to the reported `tokenToShares` division-by-zero when the divisor operand can be driven to zero by attacker-controlled input.

### Finding Description
In `program/src/math.rs`, `swap_token_amount_base_out` computes: [1](#0-0) 

For `SwapDirection::Coin2PC`, `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap()`. If `amount_out == total_pc_without_take_pnl`, `checked_sub` succeeds and yields `0` (not an overflow, since `x - x = 0`), so `denominator` becomes `0`. The next line then does `... .checked_ceil_div(denominator).unwrap()`, which internally performs a division by the `U128` value `0`. This panics the program.

The processor functions that call this math call it **before** validating that `amount_out` is strictly less than the pool's available balance: [2](#0-1) 

The bounds check `swap.amount_out >= total_pc_without_take_pnl` (or `total_coin_without_take_pnl` for the other direction) only occurs later, inside the `match swap_direction` block used for the actual token transfers: [3](#0-2) 

By that point the division has already executed and, for the boundary value `amount_out == total_*_without_take_pnl`, already panicked. The identical pattern exists in `process_swap_base_out_v2`: [4](#0-3) 

This mirrors the reported bug class exactly: a value that should be checked against a boundary condition before being used as a divisor is instead used directly, and the "protective" check is applied too late, allowing an attacker-chosen input to drive the divisor to `0`.

### Impact Explanation
Any unprivileged user calling `SwapBaseOut` / `SwapBaseOut` v2 with `amount_out` chosen to exactly equal the current `total_pc_without_take_pnl` (or `total_coin_without_take_pnl`, depending on swap direction) can force a Rust panic inside the on-chain program via `.unwrap()` on a `None` result of an internal division-by-zero. This aborts the transaction with a runtime panic rather than a controlled `ProgramError`. While this specific call reverts (no funds move because the whole instruction fails atomically), it still represents an unhandled panic path reachable from a single transaction with attacker-chosen instruction data — a robustness/availability issue for the swap-base-out code path, matching the "division by zero" bug class in the reference report. It does not by itself lead to fund loss since the transaction fails, but it demonstrates an input-validation gap (missing bound check before arithmetic) that should be fixed to avoid relying on panics/`unwrap()` for input validation, and to avoid any risk if the internal helper's behavior on the boundary value ever changes (e.g. if a future refactor changes `checked_sub`/`checked_ceil_div` semantics or ordering).

### Likelihood Explanation
Reaching the boundary condition (`amount_out` exactly equal to the pool's un-pnl balance of the destination token) is fully attacker-controlled: `amount_out` is a direct instruction argument, and `total_pc_without_take_pnl`/`total_coin_without_take_pnl` are readable on-chain state that an attacker can query before crafting the transaction. No special privileges, timing, or race conditions are required — a single transaction from any signer with any user token account is sufficient.

### Recommendation
Move the bound check (`swap.amount_out >= total_pc_without_take_pnl` for `Coin2PC`, `swap.amount_out >= total_coin_without_take_pnl` for `PC2Coin`) to occur **before** calling `Calculator::swap_token_amount_base_out`, in both `process_swap_base_out` and `process_swap_base_out_v2`, so that the invalid boundary value is rejected with a proper `AmmError` instead of reaching the division. Additionally, consider making `swap_token_amount_base_out`/`checked_ceil_div` return a `Result`/`Option` all the way up instead of relying on `.unwrap()`, so a zero divisor produces a graceful `AmmError` rather than a panic.

### Proof of Concept
1. Attacker reads on-chain `amm_pc_vault.amount` and `amm.state_data.need_take_pnl_pc` to derive `total_pc_without_take_pnl = amm_pc_vault.amount - need_take_pnl_pc` (via `Calculator::calc_total_without_take_pnl_no_orderbook`).
2. Attacker submits a `SwapBaseOut` instruction with `swap_direction = Coin2PC` (source = coin, destination = pc) and `swap.amount_out` set exactly equal to `total_pc_without_take_pnl`.
3. In `process_swap_base_out`, execution reaches:
   ```rust
   let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(
       swap.amount_out.into(),
       total_pc_without_take_pnl.into(),
       total_coin_without_take_pnl.into(),
       swap_direction,
   );
   ```
   which inside `swap_token_amount_base_out` computes `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap() = 0`, then `... .checked_ceil_div(denominator).unwrap()` — division by zero — causing the on-chain program to panic before the later `swap.amount_out >= total_pc_without_take_pnl` check (which would have rejected this input) is ever reached.
4. The transaction aborts with a runtime panic instead of a clean program error, confirming the unchecked division-by-zero path reachable purely from user-supplied instruction data.

### Citations

**File:** program/src/math.rs (L327-367)
```rust
    pub fn swap_token_amount_base_out(
        amount_out: U128,
        total_pc_without_take_pnl: U128,
        total_coin_without_take_pnl: U128,
        swap_direction: SwapDirection,
    ) -> U128 {
        let amount_in;
        match swap_direction {
            SwapDirection::Coin2PC => {
                // (x + delta_x) * (y + delta_y) = x * y
                // (coin + amount_in) * (pc - amount_out) = coin * pc
                // => amount_in = coin * pc / (pc - amount_out) - coin
                // => amount_in = (coin * pc - pc * coin + amount_out * coin) / (pc - amount_out)
                // => amount_in = (amount_out * coin) / (pc - amount_out)
                let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();
                amount_in = total_coin_without_take_pnl
                    .checked_mul(amount_out)
                    .unwrap()
                    .checked_ceil_div(denominator)
                    .unwrap()
            }
            SwapDirection::PC2Coin => {
                // (x + delta_x) * (y + delta_y) = x * y
                // (pc + amount_in) * (coin - amount_out) = coin * pc
                // => amount_out = coin - coin * pc / (pc + amount_in)
                // => amount_out = (coin * pc + coin * amount_in - coin * pc) / (pc + amount_in)
                // => amount_out = coin * amount_in / (pc + amount_in)

                // => amount_in = coin * pc / (coin - amount_out) - pc
                // => amount_in = (coin * pc - pc * coin + pc * amount_out) / (coin - amount_out)
                // => amount_in = (pc * amount_out) / (coin - amount_out)
                let denominator = total_coin_without_take_pnl.checked_sub(amount_out).unwrap();
                amount_in = total_pc_without_take_pnl
                    .checked_mul(amount_out)
                    .unwrap()
                    .checked_ceil_div(denominator)
                    .unwrap()
            }
        }
        return amount_in;
    }
```

**File:** program/src/processor.rs (L2172-2211)
```rust
        let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(
            swap.amount_out.into(),
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        );
        // swap_in_after_add_fee * (1 - 0.0025) = swap_in_before_add_fee
        // swap_in_after_add_fee = swap_in_before_add_fee / (1 - 0.0025)
        let swap_in_after_add_fee = swap_in_before_add_fee
            .checked_mul(amm.fees.swap_fee_denominator.into())
            .unwrap()
            .checked_ceil_div(
                (amm.fees
                    .swap_fee_denominator
                    .checked_sub(amm.fees.swap_fee_numerator)
                    .unwrap())
                .into(),
            )
            .unwrap()
            .as_u64();
        encode_ray_log(SwapBaseOutLog {
            log_type: LogType::SwapBaseOut.into_u8(),
            max_in: swap.max_amount_in,
            amount_out: swap.amount_out,
            direction: swap_direction as u64,
            user_source: user_source.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            deduct_in: swap_in_after_add_fee,
        });
        if user_source.amount < swap_in_after_add_fee {
            return Err(AmmError::InsufficientFunds.into());
        }
        if swap.max_amount_in < swap_in_after_add_fee {
            return Err(AmmError::ExceededSlippage.into());
        }
        if swap_in_after_add_fee == 0 || swap.amount_out == 0 {
            return Err(AmmError::InvalidInput.into());
        }

```

**File:** program/src/processor.rs (L2212-2239)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source coin to amm_coin_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_source_owner.clone(),
                    swap_in_after_add_fee,
                )?;
                // withdraw amm_pc_vault to destination pc
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap.amount_out,
                )?;
            }
            SwapDirection::PC2Coin => {
                if swap.amount_out >= total_coin_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/processor.rs (L2551-2596)
```rust
        let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(
            swap.amount_out.into(),
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        );
        // swap_in_after_add_fee * (1 - 0.0025) = swap_in_before_add_fee
        // swap_in_after_add_fee = swap_in_before_add_fee / (1 - 0.0025)
        let swap_in_after_add_fee = swap_in_before_add_fee
            .checked_mul(amm.fees.swap_fee_denominator.into())
            .unwrap()
            .checked_ceil_div(
                (amm.fees
                    .swap_fee_denominator
                    .checked_sub(amm.fees.swap_fee_numerator)
                    .unwrap())
                .into(),
            )
            .unwrap()
            .as_u64();
        encode_ray_log(SwapBaseOutLog {
            log_type: LogType::SwapBaseOut.into_u8(),
            max_in: swap.max_amount_in,
            amount_out: swap.amount_out,
            direction: swap_direction as u64,
            user_source: user_source.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            deduct_in: swap_in_after_add_fee,
        });
        if user_source.amount < swap_in_after_add_fee {
            return Err(AmmError::InsufficientFunds.into());
        }
        if swap.max_amount_in < swap_in_after_add_fee {
            return Err(AmmError::ExceededSlippage.into());
        }
        if swap_in_after_add_fee == 0 || swap.amount_out == 0 {
            return Err(AmmError::InvalidInput.into());
        }

        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source coin to amm_coin_vault
```
