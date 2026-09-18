### Title
Unchecked division-by-zero panic in `swap_token_amount_base_out` reachable via attacker-chosen `amount_out` in `process_swap_base_out` / `process_swap_base_out_v2` - (File: `program/src/processor.rs`, `program/src/math.rs`)

### Summary
`process_swap_base_out` (and `process_swap_base_out_v2`) compute the required input amount for a base-out swap by calling `Calculator::swap_token_amount_base_out` with the attacker-supplied `swap.amount_out` **before** validating that `swap.amount_out` is strictly less than the pool's available reserve. Inside that function, the denominator of a `checked_sub` is derived directly from `total_pc_without_take_pnl - amount_out` (or `total_coin_without_take_pnl - amount_out`), and if `amount_out` exactly equals the reserve, the denominator becomes `0`, which is then fed into `checked_ceil_div`/`checked_div` and `.unwrap()`'d, causing an unhandled panic (program abort) rather than a graceful error.

### Finding Description
In `Calculator::swap_token_amount_base_out`: [1](#0-0) 

For `SwapDirection::Coin2PC` the denominator is `total_pc_without_take_pnl.checked_sub(amount_out).unwrap()`, and for `SwapDirection::PC2Coin` it is `total_coin_without_take_pnl.checked_sub(amount_out).unwrap()`. Both are then passed as the divisor to `checked_ceil_div(denominator).unwrap()`.

In `process_swap_base_out`, this function is invoked with the raw, attacker-controlled `swap.amount_out` immediately after the pool reserves are computed, and well before the guard that rejects `amount_out >= total_*_without_take_pnl`: [2](#0-1) [3](#0-2) 

The out-of-bounds check (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) only occurs later, inside the `match swap_direction` transfer branches — i.e., strictly *after* `swap_token_amount_base_out` has already executed. The same ordering exists in `process_swap_base_out_v2`: [4](#0-3) 

If an attacker submits `amount_out` exactly equal to `total_pc_without_take_pnl` (for Coin2PC) or `total_coin_without_take_pnl` (for PC2Coin), `checked_sub` produces `0` (not `None`, since the values are equal, so `unwrap()` does not fail at that point), and the subsequent `checked_ceil_div` on a zero divisor triggers a division-by-zero panic that aborts the transaction/program with undefined behavior, analogous to the ImageMagick `gem.c` divide-by-zero bug class in the external report (both stem from missing zero-denominator validation before performing a division on attacker/file-influenced input).

### Impact Explanation
Any unprivileged user can submit a single `SwapBaseOut`/`SwapBaseOutV2` instruction with a crafted `amount_out` equal to the current pool reserve of the output token. This causes the program to panic during execution instead of returning a controlled `AmmError`. While Solana's runtime will still roll back the failed transaction (so this is not a fund-theft vector), it represents an availability/robustness defect: the intended `InsufficientFunds` error path is bypassed by an earlier unchecked division, so the failure mode is an uncontrolled panic rather than the designed error handling. This matches the CVSS vector in the report (`C:N/I:N/A:H`) — no confidentiality/integrity loss, but an availability-impacting flaw in program logic.

### Likelihood Explanation
High reachability: the vulnerable computation path (`swap_token_amount_base_out`) is invoked unconditionally on every base-out swap using fully attacker-controlled `amount_out`, and the protective bounds check is placed after the vulnerable division, not before it. No privileged signer, special account, or non-default build is required — an ordinary swapper can trigger it with a single transaction by choosing `amount_out` equal to the observed vault balance minus `need_take_pnl` (both readable on-chain).

### Recommendation
Move the `amount_out >= total_pc_without_take_pnl` / `amount_out >= total_coin_without_take_pnl` bounds checks to occur *before* calling `Calculator::swap_token_amount_base_out`, and additionally harden `swap_token_amount_base_out` itself to return a `Result`/checked error (e.g., `AmmError::InsufficientFunds` or `AmmError::CheckedSubOverflow`) rather than relying on `.unwrap()` on a `checked_sub` whose result can legitimately reach zero.

### Proof of Concept
1. Observe a live pool's `amm_pc_vault.amount`, `amm_coin_vault.amount`, and `amm.state_data.need_take_pnl_pc/coin` to compute `total_pc_without_take_pnl` / `total_coin_without_take_pnl` (all public on-chain data).
2. Submit a `SwapBaseOut` (or `SwapBaseOutV2`) instruction with `swap_direction = Coin2PC` and `amount_out = total_pc_without_take_pnl` (exact reserve value).
3. `process_swap_base_out` calls `Calculator::swap_token_amount_base_out(amount_out, total_pc_without_take_pnl, total_coin_without_take_pnl, Coin2PC)` at [5](#0-4) , which computes `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` = `0`, then `checked_ceil_div(0)` — an unhandled divide-by-zero panic aborts the instruction before the `amount_out >= total_pc_without_take_pnl` guard at [6](#0-5)  is ever reached.

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

**File:** program/src/processor.rs (L2154-2177)
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
```

**File:** program/src/processor.rs (L2212-2217)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source coin to amm_coin_vault
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
