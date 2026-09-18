### Title
Silent `U128::as_u64()` truncation in `swap_base_out` lets an attacker drain a pool for near-zero payment - (File: `program/src/processor.rs`)

### Summary
`process_swap_base_out` / `process_swap_base_out_v2` compute the amount a swapper must pay (`swap_in_after_add_fee`) as a `U128` value and convert it to `u64` with the *unchecked*, truncating `.as_u64()` accessor of the `uint::construct_uint!`-generated `U128` type, instead of the crate's own bounds-checked `Calculator::to_u64()` (which uses `try_into()` and returns `AmmError::ConversionFailure` on overflow). This is the same bug class as CVE-2022-24845/GHSA-j2x6-9323-fp7h: a value that can legitimately exceed the target integer's range is never validated against those bounds before being implicitly truncated, and the truncated (wrapped) value is then trusted for security-critical checks.

### Finding Description
`Calculator::swap_token_amount_base_out` computes the required input amount as: [1](#0-0) 

For `SwapDirection::Coin2PC`, `amount_in = coin * amount_out / (pc - amount_out)` (ceiling division). Both `coin`, `pc`, and `amount_out` are attacker-influenced `u64` magnitudes, but the entire calculation is carried out in `U128` (`math.rs:341-346`). By choosing `swap.amount_out` very close to `total_pc_without_take_pnl` (but still `< total_pc_without_take_pnl`, which is only checked *after* this computation — see below), the denominator `pc - amount_out` can be driven down to `1`, making `amount_in` blow up to a value that can exceed `u64::MAX` while still safely fitting inside `U128` (max ≈ 3.4e38).

In `process_swap_base_out`, this oversized `U128` is fed straight into the fee scale-up and then truncated: [2](#0-1) 

`.as_u64()` on the `construct_uint!`-based `U128` type simply returns the low 64 bits — it does **not** panic or error when the value doesn't fit, unlike the codebase's own `Calculator::to_u64()` helper: [3](#0-2) 

The truncated (wrapped-around) `swap_in_after_add_fee` is then used for all of the actual security checks: [4](#0-3) 

and only afterward is `swap.amount_out` checked against the pool balance: [5](#0-4) 

Because the `amount_out >= total_pc_without_take_pnl` bound check happens *after* the truncation and *after* the derived `swap_in_after_add_fee` has already been validated against `user_source.amount` / `swap.max_amount_in`, an attacker can craft `amount_out` (just below `total_pc_without_take_pnl`) so that the true (un-truncated) required payment is astronomically large, but its low-64-bit remainder — the value actually enforced on-chain — is arbitrarily small. The attacker then supplies that tiny truncated amount as `user_source` balance and `max_amount_in`, and the program transfers `swap.amount_out` (near the entire pool balance of the output token) to them: [6](#0-5) 

The identical unchecked-`.as_u64()` pattern also exists in `process_swap_base_out_v2`: [7](#0-6) 

### Impact Explanation
An unprivileged swapper can trigger `SwapBaseOut`/`SwapBaseOut2` with attacker-chosen `amount_out` and `max_amount_in`, using only a single submitted transaction with no special account permissions. By selecting `amount_out` such that the wrapped `swap_in_after_add_fee` lands on a small value, they can withdraw almost the entire `pc_vault` (or `coin_vault`) balance while paying a negligible or attacker-controlled amount, resulting in direct theft of LP/pool funds and permanent insolvency of the pool (the invariant `x*y=k` is destroyed, and remaining LPs cannot redeem their share). This satisfies "concrete theft ... of user or LP funds" / "insolvent pool accounting."

### Likelihood Explanation
The vulnerable path is reachable directly through the public `SwapBaseOut` and `SwapBaseOut2` instructions available to any swapper, requiring only account setup identical to a normal swap and off-chain computation (simulation) to find an `amount_out` value that produces a favorably small truncated payment. No privileged signer, validator behavior, or non-default build is needed, making this practically exploitable once a pool has meaningful liquidity (large enough `coin`/`pc` balances for the product `coin * amount_out` to exceed `u64::MAX` before the ceiling division shrinks it back down).

### Recommendation
Replace the unchecked `.as_u64()` truncations in `Calculator::swap_token_amount_base_out`'s call sites (and the analogous ones in `swap_token_amount_base_in`) with the existing bounds-checked `Calculator::to_u64()` (or an equivalent `try_into()`/`checked_*` conversion) so that any value that cannot fit into `u64` causes the transaction to fail instead of silently wrapping. Additionally, move the `swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl` bound checks to occur *before* computing `swap_in_before_add_fee`, so the denominator can never be pathologically small.

### Proof of Concept
1. Pool has `total_coin_without_take_pnl = C` and `total_pc_without_take_pnl = P` (both attacker-observable on-chain state).
2. Attacker (off-chain) searches for a `amount_out = P - d` for small `d` (e.g., `d = 1, 2, 3, ...`) such that:
   `amount_in_raw = ceil(C * amount_out / d)`
   `swap_in_after_add_fee = ceil(amount_in_raw * fee_denominator / (fee_denominator - fee_numerator)) mod 2^64`
   is a very small number (e.g., ≤ attacker's token balance, say 1 lamport).
3. Attacker submits `process_swap_base_out` (or `_v2`) with `swap.amount_out = P - d` and `swap.max_amount_in` set to at least the small truncated value found in step 2.
4. Checks at `program/src/processor.rs:2202-2210` pass trivially since `swap_in_after_add_fee` is tiny.
5. Check at `program/src/processor.rs:2214` passes because `amount_out = P - d < P`.
6. The program transfers the tiny `swap_in_after_add_fee` from the attacker into `amm_coin_vault`/`amm_pc_vault`, and transfers `swap.amount_out ≈ P` (or `≈ C`) out to the attacker (`program/src/processor.rs:2218-2234`), draining nearly the entire vault for a negligible cost.

### Citations

**File:** program/src/math.rs (L46-48)
```rust
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

**File:** program/src/processor.rs (L2202-2210)
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

**File:** program/src/processor.rs (L2212-2216)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/processor.rs (L2217-2234)
```rust
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

**File:** program/src/processor.rs (L2551-2581)
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
```
