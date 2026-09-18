Confirmed: `checked_ceil_div` at `program/src/math.rs:485-505` returns `None` on a zero divisor (via `checked_div`/`checked_rem` returning `None`), and callers immediately `.unwrap()` the result.

### Title
Attacker-controlled division-by-zero panic in `SwapBaseOut`/`SwapBaseOutV2` via `swap_token_amount_base_out` - ([File: program/src/math.rs])

### Summary
`Calculator::swap_token_amount_base_out` computes `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` (or the coin-side equivalent) and then divides by it using `.checked_ceil_div(denominator).unwrap()`. If an attacker-supplied `amount_out` exactly equals the pool's current `total_pc_without_take_pnl` (or `total_coin_without_take_pnl`), `denominator` becomes `0`, and `checked_ceil_div` returns `None` (its internal `checked_div`/`checked_rem` both return `None` on zero), causing the subsequent `.unwrap()` to panic.

### Finding Description
`process_swap_base_out` and `process_swap_base_out_v2` both call `Calculator::swap_token_amount_base_out` with the raw, unvalidated `swap.amount_out` from instruction data *before* any bound check against the pool reserves is performed: [1](#0-0) 
The bounds check `if swap.amount_out >= total_pc_without_take_pnl { return Err(...) }` only happens after this calculation, inside the `match swap_direction` block: [2](#0-1) 
Inside `swap_token_amount_base_out`, the vulnerable division is: [3](#0-2) 
and the symmetric `PC2Coin` branch: [4](#0-3) 
`checked_ceil_div` on `U128` explicitly returns `None` for a zero right-hand side: [5](#0-4) 
Since `amount_out` is directly attacker-controlled instruction data (unpacked from `SwapInstructionBaseOut`), and pool reserve totals (`total_pc_without_take_pnl`/`total_coin_without_take_pnl`) are readable on-chain state, an attacker can craft `swap.amount_out` to exactly equal the relevant reserve total, driving `denominator` to zero and triggering an `unwrap()` panic before any protective check executes.

### Impact Explanation
The panic aborts the transaction with a runtime crash (Rust panic → BPF program abort), denying service for that specific swap call. This matches the CWE-369 "Divide By Zero" class in the referenced PaddlePaddle advisory. It does not expose fund theft or freeze funds long-term (the transaction simply fails/reverts and pool state is unaffected), but it is a reachable, attacker-triggerable panic in the primary swap path (`SwapBaseOut`/`SwapBaseOutV2`) using nothing but a single transaction with attacker-chosen instruction data.

### Likelihood Explanation
High likelihood of triggering the panic condition: any unprivileged user calling `SwapBaseOut`/`SwapBaseOutV2` can read the current vault balances via `amm_coin_vault`/`amm_pc_vault` (public accounts) and craft `amount_out` equal to `total_pc_without_take_pnl` or `total_coin_without_take_pnl` at the current block. No special permissions or race conditions beyond normal instruction crafting are required.

### Recommendation
Perform the reserve-sufficiency check (`amount_out < total_pc_without_take_pnl` / `total_coin_without_take_pnl`) *before* calling `Calculator::swap_token_amount_base_out`, and/or change `swap_token_amount_base_out` to return `Option<U128>`/`Result` instead of unwrapping, propagating a proper `AmmError` (e.g., `AmmError::InsufficientFunds`) when the denominator would be zero.

### Proof of Concept
1. Read `amm_pc_vault.amount` and `amm_coin_vault.amount` for a target pool and compute `total_pc_without_take_pnl`/`total_coin_without_take_pnl` via `Calculator::calc_total_without_take_pnl_no_orderbook` (same formula used on-chain).
2. Submit a `SwapBaseOut` (or `SwapBaseOutV2`) instruction with `amount_out` set exactly equal to `total_pc_without_take_pnl` (for `Coin2PC` direction) or `total_coin_without_take_pnl` (for `PC2Coin` direction), with any `max_amount_in`.
3. Inside `process_swap_base_out`/`process_swap_base_out_v2`, `Calculator::swap_token_amount_base_out` is invoked before the `swap.amount_out >= total_..._without_take_pnl` guard executes, computing `denominator = total_..._without_take_pnl.checked_sub(amount_out).unwrap() == 0`.
4. `checked_ceil_div(0)` returns `None`; the following `.unwrap()` panics, aborting the transaction (`program/src/math.rs:345` / `:362`).

### Citations

**File:** program/src/processor.rs (L2172-2177)
```rust
        let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(
            swap.amount_out.into(),
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        );
```

**File:** program/src/processor.rs (L2212-2216)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/math.rs (L335-347)
```rust
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

**File:** program/src/math.rs (L348-364)
```rust
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
