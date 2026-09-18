### Title
Silent truncation from `U128` to `u64` via unchecked `.as_u64()` in swap math instead of checked conversion - ([File: program/src/processor.rs])

### Summary
`process_swap_base_out` (and `process_swap_base_in`) compute the token amount that determines how much the user must pay/receive using `U128` arithmetic, and then convert the final result to `u64` with the crate's `.as_u64()` method, which truncates to the low 64 bits instead of erroring on overflow. This is the same bug class as the reported `Distributor` issue — a narrowing numeric conversion performed without first validating that the value fits in the destination type — except here it silently discards bits rather than reverting.

### Finding Description
`Calculator::swap_token_amount_base_out` computes `amount_in` entirely in `U128` and can legitimately produce values that exceed `u64::MAX` when the attacker-chosen `amount_out` drives the AMM constant-product denominator close to zero: [1](#0-0) 

The caller then converts this `U128` result straight to `u64` with `.as_u64()`, which — unlike `Calculator::to_u64` (which uses `TryInto` and returns `AmmError::ConversionFailure` on overflow) — truncates silently: [2](#0-1) [3](#0-2) 

Compare this with the properly-checked conversion pattern used elsewhere in the same file, `Calculator::to_u64`, which the codebase itself defines specifically to avoid unchecked casts: [4](#0-3) 

The overflow-vulnerable value (`swap_in_after_add_fee`, truncated) is exactly the amount subsequently compared against slippage/balance checks and transferred via CPI: [5](#0-4) 

Because the truncating cast happens *before* any bounds check (mirroring the report's "cast first, check second" anti-pattern), a user-source-side underpayment can pass the `user_source.amount < swap_in_after_add_fee` and `swap.max_amount_in < swap_in_after_add_fee` checks, since those checks are evaluated against the already-truncated (wrapped) small value rather than the true, much larger required input.

The identical unchecked-cast pattern (`.as_u64()` on a `U128` swap-math result, feeding directly into a token transfer amount) is also present in `process_swap_base_in`: [6](#0-5) [7](#0-6) 

### Impact Explanation
If an attacker crafts `SwapBaseOut` with `amount_out` chosen so the constant-product denominator (`total_pc_without_take_pnl - amount_out` or `total_coin_without_take_pnl - amount_out`) is tiny, the true required input `amount_in` computed in `U128` can land in the range `(2^64, U128::MAX / fee_denominator)` — large enough to overflow `u64` but not large enough to overflow the subsequent `checked_mul` by `fees.swap_fee_denominator` (which would otherwise panic and revert). In that window, `.as_u64()` wraps the value down to an attacker-influenced small number. That truncated, drastically undercharged amount is what actually gets validated against the user's balance/slippage and transferred from the user, while the full `swap.amount_out` is paid out of the vault — breaking the constant-product invariant and allowing extraction of pool funds for far less than the correct price, directly harming LPs/the pool.

### Likelihood Explanation
Reachable in a single `SwapBaseOut` transaction from any unprivileged swapper with fully attacker-controlled `amount_out`/`max_amount_in` and account selection (source/destination token accounts, direction). No privileged signer or off-chain step is required. The main precondition is that pool reserves/`amount_out` be large enough (tens of quintillions in raw token units, plausible for high-supply/high-decimal SPL tokens) to push the intermediate `U128` computation past `u64::MAX` without overflowing `U128` itself — a magnitude-dependent but concretely reachable condition given attacker control of `amount_out` and the freedom to pick which pools/tokens to target.

### Recommendation
Replace all direct `.as_u64()` calls on `U128` swap-math results in `program/src/math.rs` and `program/src/processor.rs` with the existing checked `Calculator::to_u64(...)` helper (which returns `AmmError::ConversionFailure` via `TryInto`), and propagate the error with `?` instead of allowing silent truncation. Apply this consistently to `swap_token_amount_base_in`, `swap_token_amount_base_out`, and every downstream `.as_u64()` call in `process_swap_base_in`/`process_swap_base_out`.

### Proof of Concept
1. Attacker selects/creates a pool where `total_coin_without_take_pnl` and `total_pc_without_take_pnl` are large (near `2^60`–`2^63`, achievable with high-decimal/high-supply SPL tokens).
2. Attacker calls `SwapBaseOut` with `swap.amount_out` set just below `total_pc_without_take_pnl` (or `total_coin_without_take_pnl` for the other direction), driving `denominator = total_pc_without_take_pnl.checked_sub(amount_out)` to a very small value (e.g., `1`).
3. In `Calculator::swap_token_amount_base_out` (`program/src/math.rs:327-367`), `amount_in = total_coin_without_take_pnl * amount_out / denominator` becomes a `U128` value exceeding `2^64` but still within `U128::MAX` after the subsequent fee multiplication in `processor.rs:2180-2191`/`2559-2570`.
4. `.as_u64()` truncates this to a small attacker-favorable value, `swap_in_after_add_fee`.
5. The checks at `processor.rs:2581-2589` (`user_source.amount < swap_in_after_add_fee`, `swap.max_amount_in < swap_in_after_add_fee`) pass trivially because they compare against the truncated small value.
6. The CPI transfers `swap.amount_out` (large, real) out of the vault while only the truncated small amount is pulled from the attacker, breaking pool solvency.

### Citations

**File:** program/src/math.rs (L42-48)
```rust
    pub fn to_u128(val: u64) -> Result<u128, AmmError> {
        val.try_into().map_err(|_| AmmError::ConversionFailure)
    }

    pub fn to_u64(val: u128) -> Result<u64, AmmError> {
        val.try_into().map_err(|_| AmmError::ConversionFailure)
    }
```

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

**File:** program/src/processor.rs (L1970-1998)
```rust
        let swap_fee = U128::from(swap.amount_in)
            .checked_mul(amm.fees.swap_fee_numerator.into())
            .unwrap()
            .checked_ceil_div(amm.fees.swap_fee_denominator.into())
            .unwrap();
        let swap_in_after_deduct_fee = U128::from(swap.amount_in).checked_sub(swap_fee).unwrap();
        let swap_amount_out = Calculator::swap_token_amount_base_in(
            swap_in_after_deduct_fee,
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        )
        .as_u64();
        encode_ray_log(SwapBaseInLog {
            log_type: LogType::SwapBaseIn.into_u8(),
            amount_in: swap.amount_in,
            minimum_out: swap.minimum_amount_out,
            direction: swap_direction as u64,
            user_source: user_source.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            out_amount: swap_amount_out,
        });
        if swap_amount_out < swap.minimum_amount_out {
            return Err(AmmError::ExceededSlippage.into());
        }
        if swap_amount_out == 0 || swap.amount_in == 0 {
            return Err(AmmError::InvalidInput.into());
        }
```

**File:** program/src/processor.rs (L2172-2191)
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
```

**File:** program/src/processor.rs (L2372-2395)
```rust
        let swap_fee = U128::from(swap.amount_in)
            .checked_mul(amm.fees.swap_fee_numerator.into())
            .unwrap()
            .checked_ceil_div(amm.fees.swap_fee_denominator.into())
            .unwrap();
        let swap_in_after_deduct_fee = U128::from(swap.amount_in).checked_sub(swap_fee).unwrap();
        let swap_amount_out = Calculator::swap_token_amount_base_in(
            swap_in_after_deduct_fee,
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        )
        .as_u64();
        encode_ray_log(SwapBaseInLog {
            log_type: LogType::SwapBaseIn.into_u8(),
            amount_in: swap.amount_in,
            minimum_out: swap.minimum_amount_out,
            direction: swap_direction as u64,
            user_source: user_source.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            out_amount: swap_amount_out,
        });
        if swap_amount_out < swap.minimum_amount_out {
```

**File:** program/src/processor.rs (L2551-2570)
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
```

**File:** program/src/processor.rs (L2581-2589)
```rust
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
