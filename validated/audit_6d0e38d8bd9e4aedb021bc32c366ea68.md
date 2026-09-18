### Title
Unchecked U128→u64 truncation in `swap_token_amount_base_out` allows attacker to pay a truncated (tiny) `amount_in` while draining `amount_out` from the pool - ([File: program/src/processor.rs])

### Summary
`process_swap_base_out` and `process_swap_base_out_v2` compute the required input amount for a "swap-base-out" trade in `U128` arithmetic and then downcast the result to `u64` using the truncating `.as_u64()` conversion instead of a checked conversion. Because the attacker fully controls `swap.amount_out` (and the pool-side check for `amount_out < reserve` happens only *after* this computation and the truncated value has already been derived and used for slippage/insufficient-funds checks), an attacker can choose an `amount_out` that drives the required `amount_in` above `u64::MAX`. The truncation wraps this huge value down to an attacker-influenceable small `u64`, letting the attacker pay a token amount far smaller than economically required while still withdrawing the requested (large) `amount_out` from the pool vault.

### Finding Description
In `Calculator::swap_token_amount_base_out` (`program/src/math.rs:327-367`), for direction `Coin2PC`:
```
let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();
amount_in = total_coin_without_take_pnl.checked_mul(amount_out).unwrap().checked_ceil_div(denominator).unwrap()
``` [1](#0-0) 

`amount_in` is returned as `U128` (128-bit), with no bound tying it back to `u64`.

In `process_swap_base_out` (and the analogous `process_swap_base_out_v2`), this `U128` result is fed into a fee adjustment and then truncated with `.as_u64()`:
```rust
let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(
    swap.amount_out.into(),
    total_pc_without_take_pnl.into(),
    total_coin_without_take_pnl.into(),
    swap_direction,
);
let swap_in_after_add_fee = swap_in_before_add_fee
    .checked_mul(amm.fees.swap_fee_denominator.into())
    .unwrap()
    .checked_ceil_div(...)
    .unwrap()
    .as_u64();
``` [2](#0-1) 

The only bound check on `swap.amount_out` relative to the pool reserve (`if swap.amount_out >= total_pc_without_take_pnl { return Err(...) }`) is performed *after* `swap_in_after_add_fee` has already been computed via the truncating cast and used in the `user_source.amount < swap_in_after_add_fee` and `swap.max_amount_in < swap_in_after_add_fee` checks: [3](#0-2) 

`.as_u64()` on the `uint`-crate-style `U128` type is a truncating cast (returns the low 64 bits) rather than a checked conversion such as `Calculator::to_u64`, which uses `try_into` and returns an error on overflow: [4](#0-3) 

By choosing `amount_out` very close to `total_pc_without_take_pnl` (making the `denominator = total_pc_without_take_pnl - amount_out` very small), the attacker can inflate `amount_in = total_coin_without_take_pnl * amount_out / denominator` far past `2^64 - 1` without triggering any `checked_mul`/`checked_sub` panic (since `total_coin_without_take_pnl` and `amount_out` are both bounded `u64` values whose product safely fits in `u128`). The subsequent `.as_u64()` silently wraps this value to an attacker-predictable small number, which becomes the actual amount transferred from the user to the pool via `Invokers::token_transfer`, while the pool still pays out the full, large `swap.amount_out` to the attacker.

The identical pattern also exists in `process_swap_base_out_v2`: [5](#0-4) 

### Impact Explanation
This breaks the constant-product swap invariant and lets an unprivileged swapper drain almost all of one side of a pool's liquidity while paying only a wrapped-around, attacker-chosen small `u64` amount of the other token. This is a direct theft of LP/pool funds and results in insolvent pool accounting (the AMM vault balance no longer matches its internal state), affecting all LPs in the pool. This is High/Critical impact: unbacked withdrawal of pool funds reachable from a single transaction with attacker-chosen instruction data.

### Likelihood Explanation
High. The attack requires only a single `SwapBaseOut`/`SwapBaseOutV2` instruction with attacker-chosen `amount_out` and `max_amount_in` values, on any pool whose reserve sizes are realistic (e.g., `total_coin_without_take_pnl` in the range of 10^12–10^15 raw units, which is common for tokens with 6-9 decimals). No special privileges, validator behavior, or off-chain conditions are required — it is directly reachable by any user submitting a swap transaction with crafted parameters.

### Recommendation
Replace the truncating `.as_u64()` calls in `process_swap_base_out`/`process_swap_base_out_v2` (and any other place returning `swap_in_after_add_fee`) with the existing checked conversion `Calculator::to_u64(...)` (which uses `try_into` and returns `AmmError::ConversionFailure` on overflow), or explicitly check that `swap_in_before_add_fee`/`swap_in_after_add_fee` are `<= u64::MAX` before truncating. Additionally, perform the `amount_out < total_pc_without_take_pnl` / `amount_out < total_coin_without_take_pnl` reserve-sufficiency check *before* computing `swap_token_amount_base_out`, so a near-reserve `amount_out` cannot even reach the truncating computation.

### Proof of Concept
1. Pool state: `total_coin_without_take_pnl = 10^15`, `total_pc_without_take_pnl = 10^15` (realistic reserve sizes).
2. Attacker calls `SwapBaseOut` with `swap_direction = Coin2PC`, `amount_out = total_pc_without_take_pnl - 1000` (denominator = 1000), and `max_amount_in = u64::MAX` (or a small value matching the expected truncated result).
3. `swap_token_amount_base_out` computes:
   `amount_in ≈ 10^15 * (10^15 - 1000) / 1000 ≈ 10^27`, which comfortably fits in `u128` (no panic) but vastly exceeds `u64::MAX (~1.8×10^19)`.
4. `swap_in_after_add_fee = amount_in * fee_denominator / (fee_denominator - fee_numerator)` remains > `u64::MAX`, and `.as_u64()` truncates it to `swap_in_after_add_fee mod 2^64`, an attacker-computable small number.
5. The subsequent checks (`user_source.amount < swap_in_after_add_fee`, `swap.max_amount_in < swap_in_after_add_fee`) pass trivially because the truncated value is small.
6. `Invokers::token_transfer` moves only the small truncated `swap_in_after_add_fee` from the attacker into `amm_coin_vault`, while `Invokers::token_transfer_with_authority` pays out the full `swap.amount_out` (nearly the entire `pc` reserve) to the attacker, resulting in a massive loss of pool funds. [6](#0-5)

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

**File:** program/src/processor.rs (L2172-2234)
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
