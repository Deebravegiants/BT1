Based on my investigation, I found a concrete, reachable division-by-zero panic in the swap-base-out path.

### Title
Division-by-zero panic in `swap_token_amount_base_out` reachable via attacker-chosen `amount_out` equal to pool reserves - ([File: program/src/math.rs])

### Summary
`Calculator::swap_token_amount_base_out` computes a subtraction-based denominator from pool reserves and an attacker-supplied `amount_out`, then performs `checked_ceil_div` on it, before the caller validates that `amount_out` is strictly less than the pool reserve. Because `checked_sub` on `U128` succeeds and returns `0` when the two values are equal (rather than `None`), an attacker who sets `swap.amount_out` exactly equal to the pool's `total_pc_without_take_pnl` (or `total_coin_without_take_pnl`) causes the subsequent division to divide by zero, panicking the program mid-instruction — the same bug class as `paddle.argmin`/`argmax`'s unchecked division causing a runtime crash.

### Finding Description
In `swap_token_amount_base_out`, for `SwapDirection::Coin2PC`: [1](#0-0) 
the `denominator` is `total_pc_without_take_pnl.checked_sub(amount_out).unwrap()`. When `amount_out == total_pc_without_take_pnl`, `checked_sub` returns `Some(0)` (valid, non-negative), so `.unwrap()` does not panic here — but the following `.checked_ceil_div(denominator)` then divides by zero: [2](#0-1) 
`checked_ceil_div` calls `self.checked_div(rhs)?` — dividing by a zero `U128` returns `None` from the underlying `uint` crate's `checked_div`, and the caller immediately calls `.unwrap()` on that `Option`, causing a panic.

This function is called from `process_swap_base_out` and `process_swap_base_out_v2` with `swap.amount_out` — a fully attacker-controlled field of the instruction data — passed in *before* the guard that rejects `amount_out >= total_pc_without_take_pnl` (or `total_coin_without_take_pnl` for `PC2Coin`): [3](#0-2) [4](#0-3) 
The equality-check guard (`>=`) is only evaluated *after* the division has already occurred, so setting `amount_out` exactly equal to the pool reserve triggers the panic before the guard can reject the request. The identical pattern exists in `process_swap_base_out_v2`: [5](#0-4) [6](#0-5) 

### Impact Explanation
When triggered, the instruction panics and the entire transaction fails; Solana's runtime rolls back all state changes atomically on a failed transaction, so no token transfers, LP-minting, or accounting updates occur. The practical effect is limited to a reverted transaction for whoever submits it (or for any composing transaction/CPI caller), not persistent state corruption, fund theft, or freezing, since no writes are committed. This is a "compute-only"/no-lasting-impact revert, matching the excluded category defined by the review rules (no-impact analogs are out of scope), rather than fund theft, freezing, unbacked LP minting, or insolvent accounting.

### Likelihood Explanation
The condition is trivially reachable in a single attacker-crafted transaction: submit `SwapBaseOut`/`SwapBaseOutV2` with `amount_out` set exactly to the current `total_pc_without_take_pnl` (Coin2PC) or `total_coin_without_take_pnl` (PC2Coin), values that are readable from on-chain vault balances at any time. No special privileges are required.

### Recommendation
Move the `amount_out >= total_pc_without_take_pnl` / `>= total_coin_without_take_pnl` bounds check to occur *before* calling `swap_token_amount_base_out`, and/or change `checked_sub`/`checked_ceil_div` chains to propagate `None`/errors instead of `.unwrap()`, returning a proper `AmmError` (e.g., `InsufficientFunds` or `CalculationExRateFailure`) instead of panicking.

### Proof of Concept
1. Read the AMM's current `amm_pc_vault.amount` and `amm.state_data.need_take_pnl_pc` to derive `total_pc_without_take_pnl` (as done in `Calculator::calc_total_without_take_pnl_no_orderbook`, [7](#0-6) ).
2. Submit a `SwapBaseOut` (or `SwapBaseOutV2`) instruction with `swap_direction = Coin2PC` and `swap.amount_out` set exactly equal to `total_pc_without_take_pnl`.
3. `swap_token_amount_base_out` computes `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap() = 0`, then `.checked_ceil_div(0)` returns `None`, and the subsequent `.unwrap()` panics, aborting the instruction ( [8](#0-7) ).

### Citations

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

**File:** program/src/math.rs (L496-504)
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
```

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

**File:** program/src/processor.rs (L2591-2594)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
```
