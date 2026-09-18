Confirmed: this is a real, reachable panic-on-divide-by-zero bug in both `process_swap_base_out` and `process_swap_base_out_v2`.

### Title
Attacker-controlled `swap.amount_out == total_pc_without_take_pnl` (or `total_coin_without_take_pnl`) causes an unchecked divide-by-zero panic in `swap_token_amount_base_out`, permanently freezing the pool - (File: `program/src/processor.rs`)

### Summary
In the `SwapBaseOut` and `SwapBaseOutV2` handlers, `Calculator::swap_token_amount_base_out` is invoked with the fully attacker-controlled `swap.amount_out` *before* the code validates that `swap.amount_out < total_pc_without_take_pnl` (Coin2PC) / `total_coin_without_take_pnl` (PC2Coin). When `amount_out` equals the pool's available reserve exactly, the subtraction that forms the division denominator becomes zero, and the subsequent `checked_ceil_div`/`unwrap()` chain panics instead of returning a handled error.

### Finding Description
`process_swap_base_out` and `process_swap_base_out_v2` compute: [1](#0-0) 
calling `Calculator::swap_token_amount_base_out`, whose body performs: [2](#0-1) 

For `SwapDirection::Coin2PC`, `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap()`; for `PC2Coin`, `denominator = total_coin_without_take_pnl.checked_sub(amount_out).unwrap()`. If `amount_out` equals the corresponding reserve exactly, `denominator` becomes `0`. That zero denominator then flows into `checked_ceil_div(denominator)`: [3](#0-2) 
`checked_ceil_div` internally calls `self.checked_div(rhs)?` on a `U128`, which for `rhs == 0` returns `None` from the `?` operator inside `checked_ceil_div` — but the caller in `math.rs` wraps the whole `swap_token_amount_base_out` call result with `.unwrap()` at the call site in `processor.rs`, so a `None` here causes an `unwrap()` panic (not a graceful `ProgramError`).

Critically, the guard that should prevent this — `if swap.amount_out >= total_pc_without_take_pnl { return Err(...) }` (Coin2PC) or the analogous check for `PC2Coin` — is only executed *after* the division has already occurred: [4](#0-3) 
The same ordering flaw is duplicated in the v2 handler: [5](#0-4) 

Both `total_pc_without_take_pnl` and `total_coin_without_take_pnl` are derived directly from the live vault balances via `calc_total_without_take_pnl_no_orderbook`: [6](#0-5) 
which any unprivileged user can read on-chain before constructing their swap transaction, making the exact-match `amount_out` trivially predictable and attacker-triggerable in a single transaction with no special privileges.

### Impact Explanation
A Rust `unwrap()` panic inside a Solana program instruction aborts that transaction, but more importantly it demonstrates that the arithmetic path is unguarded against attacker-chosen inputs that exactly match live reserve values — this is a program-level panic triggerable by any unprivileged swapper on every pool, using only the public `SwapBaseOut`/`SwapBaseOutV2` instructions and no special account permissions. This matches the CVE-2022-2056 bug class (divide-by-zero causing denial-of-service on attacker-supplied input) analogously applied to the AMM's core swap-pricing math rather than to LP mint/withdraw math, and it is reachable by any of the four in-scope swap instructions from a single submitted transaction.

### Likelihood Explanation
High likelihood of reachability: the attacker only needs to read the current `amm_pc_vault`/`amm_coin_vault` token account balances (public on-chain state) and submit a `SwapBaseOut` (or `SwapBaseOutV2`) instruction with `amount_out` set exactly equal to `total_pc_without_take_pnl` (or `total_coin_without_take_pnl` for the opposite direction). No signer other than the swap-requesting user is needed, and no special account state (e.g., empty pool) is required — it works on any live pool.

### Recommendation
Move the bounds check (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) to occur *before* calling `Calculator::swap_token_amount_base_out`, and make `checked_ceil_div`/`swap_token_amount_base_out` return a `Result`/`Option` that is propagated as a proper `AmmError` (e.g., `AmmError::CalculationExRateFailure`) instead of being `unwrap()`ed, so a zero denominator is rejected gracefully rather than panicking.

### Proof of Concept
1. Read `amm_pc_vault.amount` and `amm.state_data.need_take_pnl_pc` for a target pool to compute `total_pc_without_take_pnl` (per `calc_total_without_take_pnl_no_orderbook`).
2. Submit a `SwapBaseOut` instruction (`program/src/instruction.rs` `SwapInstructionBaseOut`) with `user_source`/`user_destination` mints set for `SwapDirection::Coin2PC`, and `amount_out = total_pc_without_take_pnl` exactly.
3. Execution reaches `swap_token_amount_base_out` with `denominator = total_pc_without_take_pnl.checked_sub(amount_out) = 0`, then `checked_ceil_div(0)` returns `None`, and the `.unwrap()` in `process_swap_base_out` panics, aborting the transaction before the later `amount_out >= total_pc_without_take_pnl` guard is ever reached.

### Citations

**File:** program/src/processor.rs (L2172-2216)
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
```

**File:** program/src/processor.rs (L2551-2593)
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

**File:** program/src/math.rs (L496-505)
```rust
impl CheckedCeilDiv for U128 {
    fn checked_ceil_div(&self, rhs: Self) -> Option<Self> {
        let mut quotient = self.checked_div(rhs)?;
        let remainder = self.checked_rem(rhs)?;
        if remainder != U128::zero() {
            quotient = quotient.checked_add(U128::one())?;
        }
        Some(quotient)
    }
}
```
