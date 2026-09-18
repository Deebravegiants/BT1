Confirmed. Both `process_swap_base_out` and its v2 counterpart compute `swap_token_amount_base_out` (which internally does `checked_sub(amount_out)` then divides by that result) **before** validating `swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`. This ordering issue is the same class of bug as the external report: a legitimate, attacker-reachable input (`amount_out` exactly equal to the pool's available liquidity for the output side) drives a denominator to zero inside a `.unwrap()` chain, causing a Rust panic (arithmetic/`unwrap`-on-`None`) instead of a controlled program error — a pure, low-cost denial-of-service on the swap path triggered from a single permissionless transaction.

### Title
Panic revert (DoS) in SwapBaseOut due to zero-denominator division reachable before liquidity validation - (File: program/src/processor.rs)

### Summary
`process_swap_base_out` (and `process_swap_base_out2`) call `Calculator::swap_token_amount_base_out` to compute the required input amount **before** checking that `swap.amount_out` is less than the pool's available liquidity (`total_pc_without_take_pnl` / `total_coin_without_take_pnl`). When an unprivileged swapper submits `amount_out` exactly equal to the available pool liquidity for the requested output token, the internal calculation subtracts `amount_out` from the pool total, producing a denominator of `0`, which is then fed into a `checked_div`/`checked_ceil_div` call chained with `.unwrap()`. Since `checked_div(0)` returns `None`, the `.unwrap()` panics, aborting the transaction with a runtime panic rather than a graceful program error.

### Finding Description
The vulnerable computation lives in `Calculator::swap_token_amount_base_out`: [1](#0-0) 

For `SwapDirection::Coin2PC`, `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap()`. If `amount_out == total_pc_without_take_pnl`, `checked_sub` succeeds (returns `0`, since there's no underflow), so `denominator = 0`. The subsequent `.checked_mul(amount_out).unwrap().checked_ceil_div(denominator).unwrap()` then hits `checked_div(0)` → `None` → `.unwrap()` panics.

This function is invoked in `process_swap_base_out` at: [2](#0-1) 

Critically, the guard that would reject `amount_out >= total_pc_without_take_pnl` (or `total_coin_without_take_pnl` for the reverse direction) is only checked *after* this calculation, inside the `match swap_direction` block: [3](#0-2) 

The identical pattern exists in the "v2" variant of the instruction: [4](#0-3) [5](#0-4) 

Because the order-of-operations check happens too late, an attacker-chosen `amount_out` equal to the pool's current available balance drives the panic before the program ever reaches the intended `InsufficientFunds` error path.

### Impact Explanation
A panicking instruction aborts the whole transaction non-gracefully. While a panic and a normal `Err` return both ultimately fail the transaction (so this specific case doesn't directly steal funds), it is a functional/availability bug of the same root-cause class flagged in the external report ("exposed to a panic revert... in some valid cases" due to a missing zero-amount/zero-denominator check). It demonstrates that swap math is not fully guarded against edge-case inputs before arithmetic is performed, and confirms the validation ordering is unsafe: any legitimate, permissionless caller can trigger this panic by choosing `amount_out` equal to the current pool reserve of the output token, which is fully attacker-observable and attacker-controlled from on-chain state (vault balances) in a single instruction.

### Likelihood Explanation
High likelihood of triggering: the attacker only needs to read the current AMM vault balances (public accounts) and submit a `SwapBaseOut`/`SwapBaseOut2` instruction with `amount_out` set exactly equal to `total_pc_without_take_pnl` or `total_coin_without_take_pnl`. No special privileges, races, or unusual build flags are required — a single transaction from any user account with a valid source/destination token account suffices.

### Recommendation
Move the liquidity sufficiency checks (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) to occur immediately after computing `total_pc_without_take_pnl`/`total_coin_without_take_pnl` and *before* calling `Calculator::swap_token_amount_base_out`. Additionally, harden `swap_token_amount_base_out` (and `swap_token_amount_base_in`) to use `checked_sub`/`checked_div` with explicit `AmmError` propagation instead of `.unwrap()`, so that any degenerate zero-denominator case returns a controlled program error rather than panicking.

### Proof of Concept
1. Attacker queries the AMM's `amm_pc_vault` token account balance and the AMM state to derive `total_pc_without_take_pnl` (pool PC minus `need_take_pnl_pc`).
2. Attacker submits a `SwapBaseOut` instruction (`SwapDirection::Coin2PC`) with `swap.amount_out` set exactly equal to `total_pc_without_take_pnl`.
3. `process_swap_base_out` computes `swap_in_before_add_fee = Calculator::swap_token_amount_base_out(amount_out, total_pc_without_take_pnl, total_coin_without_take_pnl, Coin2PC)`.
4. Inside that function, `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` evaluates to `0`.
5. `total_coin_without_take_pnl.checked_mul(amount_out).unwrap().checked_ceil_div(0).unwrap()` panics because `checked_div(0)` returns `None`.
6. The transaction aborts with a Rust panic instead of returning `AmmError::InsufficientFunds`, confirming the reachable panic path prior to the intended validation.

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

**File:** program/src/processor.rs (L2591-2595)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```
