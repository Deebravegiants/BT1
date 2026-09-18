### Title
Truncating `U128` to `u64` via `.as_u64()` in `swap_token_amount_base_out` fee computation allows attacker to drain pool funds - (File: `program/src/processor.rs`)

### Summary
`process_swap_base_out` (and its `_v2` variant) compute the required input amount for a base-out swap using 128-bit arithmetic and then narrow the result to `u64` with the `uint` crate's `.as_u64()`, which silently truncates the value (keeps only the low 64 bits) instead of checking that the high bits are zero, exactly the same bug class as the `hexToAddress` finding where a `bytes32` is narrowed to `address` without validating the discarded upper bits are zero.

### Finding Description
In `Calculator::swap_token_amount_base_out` (`program/src/math.rs:327-367`), the required input amount is computed entirely in `U128`: [1](#0-0) 

This `U128` result then flows into `process_swap_base_out`: [2](#0-1) 

`swap_in_before_add_fee` and the subsequent `checked_mul`/`checked_ceil_div` operate on `U128`, but the final `.as_u64()` call performs an unchecked narrowing cast (the `uint` crate's `as_u64()` simply drops the upper 64 bits; it neither panics nor errors when they are non-zero — unlike `Calculator::to_u64`, which is used elsewhere in the same file via `TryInto` and does reject overflow, e.g. `program/src/math.rs:46-48`). This is the identical root cause as the external report: a wide integer type is reduced to a narrower one without verifying the discarded bits are zero.

The only bound on `amount_out` at this point is `swap.amount_out < total_coin_without_take_pnl` (or `total_pc_without_take_pnl` for the other direction), checked *after* `swap_in_after_add_fee` is already computed: [3](#0-2) 

That still permits the denominator `total_X_without_take_pnl - amount_out` to be as small as `1`, while the numerator `total_Y_without_take_pnl * amount_out` can be very large. With sufficiently large pool balances (both are attacker-visible `u64` vault amounts, up to `u64::MAX ≈ 1.8e19`), `swap_in_before_add_fee` (and the subsequently fee-adjusted `swap_in_after_add_fee`) can legitimately exceed `u64::MAX` while still fitting comfortably inside `U128` (max ≈ 3.4e38), so the `checked_mul`/`checked_ceil_div` calls succeed without panicking. The final `.as_u64()` then wraps the true (huge) required input amount down to an attacker-influenceable small residual value modulo 2^64.

### Impact Explanation
The truncated, wrapped `swap_in_after_add_fee` is used for both:
- the funds-sufficiency check `user_source.amount < swap_in_after_add_fee` (`program/src/processor.rs:2202-2204`)
- the slippage check `swap.max_amount_in < swap_in_after_add_fee` (`program/src/processor.rs:2205-2207`)
- the actual amount debited from the user via `Invokers::token_transfer` (`program/src/processor.rs:2218-2224`, `2242-2248`)

Because the wrapped value can be far smaller than the true required input, an attacker can pass both checks while depositing only a token amount of `swap_in_after_add_fee` (which they fully control by choosing `swap.amount_out`), yet receive the full, large `swap.amount_out` withdrawn from the pool vault via `Invokers::token_transfer_with_authority` (`program/src/processor.rs:2226-2234`, `2250-2258`). This breaks the constant-product invariant, permanently draining vault funds and insolvently mis-accounting `total_pc_without_take_pnl`/`total_coin_without_take_pnl`, i.e., direct theft of LP/pool funds.

### Likelihood Explanation
This is reachable directly via the standard `SwapBaseOut` / `SwapBaseOutV2` instructions with attacker-chosen `amount_out` and `max_amount_in`, and requires no privileged signer, no malicious validator, and no off-chain component — a single transaction from any unprivileged swapper suffices. The only precondition is that pool vault balances (attacker-observable, and to some degree attacker-influenceable through prior deposits) are large enough, together with a favorable choice of `amount_out` close to the opposite side's total, to push the U128 intermediate result above `u64::MAX` while staying under `U128::MAX`. This is plausible for pools holding tokens with high raw (undecimalized) supply/decimals, making the likelihood non-trivial though pool-size dependent.

### Recommendation
Replace the unchecked `.as_u64()` calls that finalize `swap_in_after_add_fee` (and the analogous ones in `process_swap_base_out_v2`, `process_swap_base_in`, `process_swap_base_in_v2`) with `Calculator::to_u64(...)` (or an equivalent `TryInto<u64>`/`checked_...` conversion) so that any value exceeding `u64::MAX` causes the instruction to fail with `AmmError::ConversionFailure` rather than silently wrapping.

### Proof of Concept
1. Attacker (or a colluding prior depositor) ensures the AMM pool's `total_pc_without_take_pnl` and `total_coin_without_take_pnl` are large `u64` values (e.g., both close to `u64::MAX` order of magnitude, achievable with high-decimal/high-supply mints).
2. Attacker calls `SwapBaseOut` (`process_swap_base_out`, `program/src/processor.rs:2053`) with `swap.amount_out` set to `total_coin_without_take_pnl - 1` (or `- k` for small `k`) and `swap.max_amount_in` set to a small value they are willing to pay.
3. `Calculator::swap_token_amount_base_out` computes `amount_in = total_pc_without_take_pnl * amount_out / 1` (denominator ≈ 1), a huge `U128` value that, after the fee multiplication (`program/src/processor.rs:2180-2191`), exceeds `u64::MAX` but stays below `U128::MAX`.
4. `.as_u64()` (`program/src/processor.rs:2191`) truncates this huge value down to a small wrapped `u64`, which passes both the `user_source.amount` and `swap.max_amount_in` checks.
5. The program transfers the attacker's small truncated `swap_in_after_add_fee` into the pool vault, then transfers the full, large `swap.amount_out` out of the opposite vault to the attacker (`program/src/processor.rs:2226-2234`), draining the pool.

### Citations

**File:** program/src/math.rs (L341-347)
```rust
                let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();
                amount_in = total_coin_without_take_pnl
                    .checked_mul(amount_out)
                    .unwrap()
                    .checked_ceil_div(denominator)
                    .unwrap()
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

**File:** program/src/processor.rs (L2236-2239)
```rust
            SwapDirection::PC2Coin => {
                if swap.amount_out >= total_coin_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```
