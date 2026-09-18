### Title
`process_swap_base_out` silently truncates `swap_in_after_add_fee` via unchecked `U128::as_u64()` instead of reverting on overflow - ([File: program/src/processor.rs])

### Summary
The reported Hats Protocol bug is a class of "silent wrong value instead of revert": a function that should fail on an out-of-range/edge input instead returns an incorrect but plausible-looking value, which downstream logic (or callers) trust. Raydium's `process_swap_base_out` has the same bug class: the swap-input calculation is done in `U128` arithmetic and then converted to `u64` with the *unchecked*, truncating `.as_u64()` cast rather than the checked `Calculator::to_u64()` helper that is used everywhere else in `math.rs` for this exact purpose.

### Finding Description
`Calculator::swap_token_amount_base_out` computes `amount_in` in `U128` space using unbounded multiplication/division of pool reserves and the user-chosen `amount_out`: [1](#0-0) 

In `process_swap_base_out`, the result is fed through a fee-adjustment computation and then converted directly with `.as_u64()`, which is the raw uint-crate truncating cast (keeps only the low 64 bits), unlike `Calculator::to_u64()` which is a checked `try_into()` that errors on overflow: [2](#0-1) 

Compare this to the rest of `math.rs`, where every other u64 narrowing conversion is routed through the checked helper: [3](#0-2) [4](#0-3) 

Because `total_pc_without_take_pnl`/`total_coin_without_take_pnl` (u64 reserves) and `amount_out` (attacker-controlled u64) are multiplied together and divided by a potentially very small denominator (`total_pc_without_take_pnl - amount_out` or `total_coin_without_take_pnl - amount_out`, which the attacker can drive close to zero by choosing `amount_out` close to the reserve), the intermediate `U128` value for `swap_in_before_add_fee`/`swap_in_after_add_fee` can legitimately exceed `u64::MAX`. Instead of reverting (as `Calculator::to_u64` would via `AmmError::ConversionFailure`), `.as_u64()` wraps the value down to an arbitrary, much smaller `u64`.

### Impact Explanation
The truncated (and therefore silently wrong, much smaller) `swap_in_after_add_fee` is what the caller checks against `swap.max_amount_in` and is what actually gets transferred from the user into `amm_coin_vault`/`amm_pc_vault`: [5](#0-4) 

Since the truncated value can be far smaller than the economically correct input amount required to produce `swap.amount_out`, an attacker can pass a tiny `max_amount_in`, pay a tiny (or degenerate) amount of tokens, and still receive the full requested `amount_out` from the vault. That directly drains reserves — an insolvent pool / theft of LP funds, reachable from the permissionless `SwapBaseOut` instruction with attacker-chosen `amount_out`.

### Likelihood Explanation
Reachable by any unprivileged user via a single `SwapBaseOut` transaction; no privileged signer or off-chain step required. It does require the attacker to pick an `amount_out` that drives the denominator small enough to push the U128 intermediate above `u64::MAX`, which needs sufficiently large pool reserves/decimals combinations, but this is within the attacker's control given permissionless instruction data.

### Recommendation
Replace the unchecked `.as_u64()` truncating casts in `process_swap_base_out` (and audit all other `.as_u64()` call sites in `program/src/processor.rs`) with the checked `Calculator::to_u64()` helper (or an equivalent `try_into().map_err(...)`) so that any value that cannot fit in `u64` causes the instruction to revert with `AmmError::ConversionFailure`, rather than silently substituting an incorrect small value.

### Proof of Concept
1. Attacker calls `SwapBaseOut` with `amount_out` set very close to `total_pc_without_take_pnl` (or `total_coin_without_take_pnl` for the other direction), driving the denominator in `swap_token_amount_base_out` toward a very small non-zero value.
2. `swap_in_before_add_fee` / `swap_in_after_add_fee` computed in `U128` becomes larger than `u64::MAX`.
3. `.as_u64()` at `program/src/processor.rs:2191` truncates this to a small `u64`.
4. Attacker sets `swap.max_amount_in` to this truncated (small) value so the `swap.max_amount_in < swap_in_after_add_fee` check passes.
5. `Invokers::token_transfer` moves only the truncated small amount from the attacker while `Invokers::token_transfer_with_authority` pays out the full requested `amount_out`, draining the pool. [6](#0-5)

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

**File:** program/src/math.rs (L80-94)
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
```

**File:** program/src/math.rs (L327-347)
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
```

**File:** program/src/processor.rs (L2154-2192)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        let swap_direction;
        if user_source.mint == amm_coin_vault.mint && user_destination.mint == amm_pc_vault.mint {
            swap_direction = SwapDirection::Coin2PC
        } else if user_source.mint == amm_pc_vault.mint
            && user_destination.mint == amm_coin_vault.mint
        {
            swap_direction = SwapDirection::PC2Coin
        } else {
            return Err(AmmError::InvalidUserToken.into());
        }

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
```

**File:** program/src/processor.rs (L2581-2636)
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
                // deposit source pc to amm_pc_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_source_owner.clone(),
                    swap_in_after_add_fee,
                )?;
                // withdraw amm_coin_vault to destination coin
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap.amount_out,
                )?;
```
