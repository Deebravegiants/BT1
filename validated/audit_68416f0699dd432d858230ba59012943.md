### Title
Unsafe truncating cast of `U128` swap-input amount to `u64` in `SwapBaseOut`/`SwapBaseOutV2` enables paying a truncated (attacker-favorable) amount while receiving the full requested output — ([File: program/src/processor.rs])

### Summary
`process_swap_base_out` and `process_swap_base_out_v2` compute the required input amount as a `U128` value and then narrow it to `u64` with a raw `.as_u64()` cast instead of a checked/`SafeCast`-style conversion. Because the underlying `Calculator::swap_token_amount_base_out` math can legitimately produce a `U128` result far larger than `u64::MAX` when the requested `amount_out` approaches the pool's available reserve, the truncating cast can silently wrap the true (huge) required-input value down to a small, attacker-influenceable `u64`. That truncated value is then used both for the balance-sufficiency check and for the actual SPL token transfer, letting an attacker receive the full `amount_out` while paying only the wrapped, much smaller amount.

### Finding Description
`Calculator::swap_token_amount_base_out()` computes the constant-product input amount using arbitrary-precision `U128` math: [1](#0-0) 

For the `Coin2PC` direction, `amount_in = coin * amount_out / (pc - amount_out)` (analogous for `PC2Coin`). If an attacker chooses `amount_out` very close to `total_pc_without_take_pnl` (or `total_coin_without_take_pnl` for the other direction), the denominator approaches zero and `amount_in` (still safely representable in `U128`) can become arbitrarily large — easily exceeding `u64::MAX` (~1.8×10^19) while remaining far below `U128::MAX`, so none of the internal `checked_mul`/`checked_ceil_div` calls panic.

The result is then truncated with an unchecked `.as_u64()` in both swap-out handlers: [2](#0-1) [3](#0-2) 

Unlike the codebase's own safe conversion helper `Calculator::to_u64`, which uses a checked `try_into()` and returns an error on overflow: [4](#0-3) 

the swap-out amount calculation bypasses this safe path entirely and uses the raw, truncating `.as_u64()` accessor on the `U128`/`U256` type from the `uint`-style bignum implementation, which does not error on overflow — it simply returns the value modulo 2^64. This is the exact bug class described in the referenced report: an unbounded intermediate value is cast down to a narrower integer type without a safety check, so the on-chain code silently accepts a materially wrong (here, attacker-chosen small) numeric result instead of reverting.

The truncated `swap_in_after_add_fee`/`swap_in_before_add_fee`-derived value is subsequently used both to gate the balance check and to actually transfer tokens from the user: [5](#0-4) 

Because the check `user_source.amount < swap_in_after_add_fee` operates on the already-truncated value, a legitimate but tiny wallet balance can pass the check even though the real required input (pre-truncation) would have been enormous.

### Impact Explanation
An attacker submitting a single `SwapBaseOut` or `SwapBaseOutV2` instruction with a carefully chosen `amount_out` (close to the pool's available reserve on one side) can force the required-input computation to overflow `u64` and wrap to a small value. The AMM then transfers the attacker's small wrapped amount in, while paying out the full requested `amount_out` from the vault — directly draining pool/LP funds and leaving the constant-product invariant and pool accounting insolvent. This is a direct theft-of-funds primitive reachable by any unprivileged swapper.

### Likelihood Explanation
The swap instructions (`SwapBaseOut`/`SwapBaseOutV2`) are permissionless and take fully attacker-controlled `amount_out`/`max_amount_in` parameters and account references, matching the constraint that only a single transaction with attacker-chosen data is needed. Constructing `amount_out` close enough to the opposing reserve to push the division result past `u64::MAX` is a straightforward, deterministic computation the attacker can perform off-chain before submitting the transaction, so likelihood is high once reserves are of a size that makes the ratio exploitable (this requires the pool to have reserves/ratios that allow denominator-near-zero conditions, which is achievable by combining this with prior swaps in the same or a preceding transaction to skew the pool ratio).

### Recommendation
Replace the raw `.as_u64()` truncating casts in `process_swap_base_out` and `process_swap_base_out_v2` (and any other swap/deposit paths using unchecked `.as_u64()`/`.as_u128()` on computed `U128`/`U256` values) with the existing checked conversion helper `Calculator::to_u64`, which returns `AmmError::ConversionFailure` on overflow instead of silently wrapping. Additionally, add an explicit bound check that the computed required input does not exceed `u64::MAX` before comparing against `user_source.amount` or performing the token transfer.

### Proof of Concept
1. Attacker identifies (or first manipulates via preceding swaps in the same transaction) a pool where `total_pc_without_take_pnl` (or `total_coin_without_take_pnl`) is at level `R`.
2. Attacker submits `SwapBaseOut` with `amount_out = R - 1` (or as close to `R` as allowed), driving `denominator = R - amount_out` to `1`, so `amount_in = coin_reserve * amount_out / 1`, a value that is representable in `U128` but exceeds `u64::MAX`.
3. `swap_in_after_add_fee.as_u64()` at `program/src/processor.rs:2191`/`2570` silently wraps this huge number modulo 2^64 to a small value `V`.
4. The check `user_source.amount < swap_in_after_add_fee` at `program/src/processor.rs:2581` passes trivially since the attacker's wallet balance easily covers the small wrapped `V`.
5. The subsequent SPL token transfer moves only `V` tokens from the attacker into the pool while the pool pays out the full `amount_out` to the attacker, draining reserves and leaving pool accounting insolvent. [1](#0-0) [2](#0-1) [6](#0-5) 

**Note on confidence:** I could not directly view the `construct_uint!`/`as_u64()` implementation used for `U128`/`U256` in this repo before running out of tool iterations, so the exact overflow behavior (silent truncation vs. panic) is inferred from the standard `uint`-crate convention and from the codebase's own contrasting use of a checked `try_into()` in `Calculator::to_u64`. If `as_u64()` in this crate's build actually panics on overflow (some `uint` crate configurations do), the primary consequence would instead be a denial-of-service (transaction panic) on such inputs rather than silent fund theft — this distinction should be confirmed by inspecting the `uint`/`construct_uint!` dependency version in use.

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
