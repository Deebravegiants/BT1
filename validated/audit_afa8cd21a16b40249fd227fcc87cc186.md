### Title
Division-by-zero panic in `swap_token_amount_base_out` when `amount_out` equals available reserves — ([File: program/src/math.rs])

### Summary
`process_swap_base_out` and `process_swap_base_out_v2` compute the required input amount via `Calculator::swap_token_amount_base_out` **before** validating that `swap.amount_out` is strictly less than the pool's available reserve. An attacker can pick `amount_out` exactly equal to `total_pc_without_take_pnl` (or `total_coin_without_take_pnl`), driving the denominator of a `checked_ceil_div`/`checked_sub` chain to zero and causing an `unwrap()` panic (transaction abort) instead of a graceful error — the same root-cause class as the reported Surge Protocol "Div by 0" issue: an unvalidated denominator that can be zero given attacker-chosen, in-range input.

### Finding Description
`Calculator::swap_token_amount_base_out` in [1](#0-0)  computes:

- For `SwapDirection::Coin2PC`: `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap()`, then divides `total_coin_without_take_pnl * amount_out` by this denominator via `checked_ceil_div`.
- For `SwapDirection::PC2Coin`: `denominator = total_coin_without_take_pnl.checked_sub(amount_out).unwrap()`, analogous division.

In `process_swap_base_out` (SwapBaseOut / v1) this call happens at [2](#0-1)  — **before** the reserve-sufficiency check that occurs afterwards at [3](#0-2)  (`if swap.amount_out >= total_pc_without_take_pnl { return Err(...) }` / same for coin). The same ordering exists in the V2 path at [4](#0-3) .

Because the sufficiency check is performed only *after* the division has already executed, an attacker who submits `amount_out == total_pc_without_take_pnl` (Coin2PC) or `amount_out == total_coin_without_take_pnl` (PC2Coin) causes `checked_sub` to yield `0`, which is then used as the divisor in `checked_ceil_div`. `checked_ceil_div`/`checked_div` on a zero divisor return `None`, and the surrounding `.unwrap()` panics, aborting the transaction with a runtime panic rather than a controlled program error.

This mirrors the reported bug class exactly: a value that is supposed to be constrained away from a boundary (here, `amount_out < reserve`) is validated only *after* it is already used as a denominator, so an attacker-reachable, single-instruction, fully attacker-controlled input (`amount_out`, `max_amount_in`) can force a division by zero.

### Impact Explanation
Although the panic aborts the transaction (no direct fund loss occurs from this specific call since Solana runtime reverts on panic), this qualifies as a Medium-severity issue matching the report's class: it is a denial-of-service on the `SwapBaseOut`/`SwapBaseOutV2` instructions for any pool where reserves are small enough to be griefed, and more importantly it demonstrates a broken invariant-check ordering in security-critical swap math — the reserve check exists specifically to prevent invalid/degenerate states but is placed after the computation it is meant to guard. Any future refactor that removes the `.unwrap()` panic-safety net (e.g., replaces `unwrap()` with silent wraparound, or reorders code) could turn this into a real accounting or fund-safety bug. As written, it is at minimum an availability issue against `SwapBaseOut` on thin/newly created pools, exploitable by any unprivileged swapper with attacker-chosen instruction data.

### Likelihood Explanation
High likelihood of reachability: `amount_out` and `max_amount_in` are fully attacker-controlled instruction parameters for `SwapBaseOut`/`SwapBaseOutV2`, requiring only a single transaction with normal swap accounts (no privileged signer). The condition `amount_out == total_pc_without_take_pnl` (or `total_coin_without_take_pnl`) is easily achievable by reading current vault balances (public account data) before submitting the swap instruction.

### Recommendation
Move the reserve-sufficiency check (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) to **before** calling `Calculator::swap_token_amount_base_out`, for both `process_swap_base_out` and `process_swap_base_out_v2`. Additionally, harden `swap_token_amount_base_out` itself to use `checked_sub` combined with an explicit zero-check (returning a proper `AmmError`) instead of relying on `.unwrap()` panics for boundary conditions.

### Proof of Concept
1. Attacker reads the AMM's `amm_pc_vault` and `amm_coin_vault` balances to determine `total_pc_without_take_pnl` (via `calc_total_without_take_pnl_no_orderbook`).
2. Attacker submits `SwapBaseOut` (or `SwapBaseOutV2`) with `swap_direction = Coin2PC` and `amount_out = total_pc_without_take_pnl` (exact current reserve value) and any `max_amount_in`.
3. Inside `process_swap_base_out`, `Calculator::swap_token_amount_base_out` is invoked with `amount_out == total_pc_without_take_pnl`, so `total_pc_without_take_pnl.checked_sub(amount_out) == 0`.
4. `checked_ceil_div(0)` returns `None`; the subsequent `.unwrap()` at [5](#0-4)  panics, aborting the transaction before the later reserve check at [6](#0-5)  is ever reached.

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

**File:** program/src/processor.rs (L2172-2177)
```rust
        let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(
            swap.amount_out.into(),
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        );
```

**File:** program/src/processor.rs (L2212-2239)
```rust
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
```

**File:** program/src/processor.rs (L2551-2556)
```rust
        let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(
            swap.amount_out.into(),
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        );
```
