Confirmed: `swap_token_amount_base_out` is called with an attacker-controlled `swap.amount_out` **before** the corresponding sufficiency check (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`), which only runs afterward at lines 2593/2427. This mirrors the reported bug class: an unchecked subtraction executed on a value that can legitimately exceed the minuend, causing a panic instead of a graceful, ordered validation.

### Title
Unvalidated user-supplied `amount_out` causes arithmetic-underflow panic in `swap_token_amount_base_out` before reserve-sufficiency check - (File: program/src/math.rs, program/src/processor.rs)

### Summary
`Calculator::swap_token_amount_base_out` subtracts the caller-supplied `amount_out` from the pool reserve (`total_pc_without_take_pnl` or `total_coin_without_take_pnl`) using `.checked_sub(amount_out).unwrap()` [1](#0-0) [2](#0-1) . This function is invoked from `process_swap_base_out` / `process_swap_base_out_v2` with `swap.amount_out` supplied directly by the transaction, prior to the reserve-sufficiency check that would normally reject an out-of-range value [3](#0-2) , with the guard only appearing afterward at [4](#0-3) .

### Finding Description
In `swap_token_amount_base_out`, for `SwapDirection::Coin2PC` the code computes `let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();` and for `SwapDirection::PC2Coin` it computes `let denominator = total_coin_without_take_pnl.checked_sub(amount_out).unwrap();` [5](#0-4) . Both `total_pc_without_take_pnl`/`total_coin_without_take_pnl` and `amount_out` (`swap.amount_out`) are plain values with no prior relationship enforced — nothing before this call guarantees `amount_out < reserve`. The actual sufficiency check (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) is performed only after this arithmetic, at the bottom of `process_swap_base_out` [4](#0-3)  and `process_swap_base_out_v2` at the analogous location. Any unprivileged caller of the `SwapBaseOut` instruction can pass an `amount_out` greater than or equal to the pool's available reserve for the requested output token, triggering the `.unwrap()` panic during `checked_sub` and reverting the transaction with an unhandled panic message instead of the intended `AmmError::InsufficientFunds`.

### Impact Explanation
The panic itself only aborts the single transaction (transaction failure, no state change persists), so this does not directly cause fund loss or permanent freezing on its own — Solana transaction failures are atomic and revert all state changes. However, it is a genuine violation of intended control flow: the program is designed to reject invalid `amount_out` values gracefully via a dedicated `AmmError::InsufficientFunds` error, but instead panics via an uncontrolled arithmetic underflow, matching exactly the root-cause pattern described in the reference report (unchecked subtraction executed against untrusted/attacker-influenced input prior to the intended bounds check). This is a High-confidence code-quality/robustness defect reachable by any unprivileged swapper with a single transaction and attacker-chosen `amount_out`, but based on the code reviewed, it does not by itself produce concrete theft, unbacked LP minting, insolvent accounting, or permanent freezing of funds — the failure mode is limited to a reverted transaction (denial of that specific call), not persistent damage.

### Likelihood Explanation
Trivially reachable: any user can call `SwapBaseOut`/`SwapBaseOut2` with `amount_out` set to a value at or above current pool reserves, no special privileges or preconditions required.

### Recommendation
Move the reserve-sufficiency check (`swap.amount_out < total_pc_without_take_pnl` / `total_coin_without_take_pnl`) to occur before calling `Calculator::swap_token_amount_base_out`, or replace the `.unwrap()` calls on `checked_sub` in `swap_token_amount_base_out` with a proper `ok_or(AmmError::CheckedSubOverflow)?` so all failure paths return a defined program error rather than panicking.

### Proof of Concept
1. Attacker identifies an AMM pool via `AmmInfo` and reads current `total_pc_without_take_pnl` (derivable from `amm_pc_vault.amount` minus `amm.state_data.need_take_pnl_pc`).
2. Attacker submits a `SwapBaseOut` instruction (`swap_direction = Coin2PC`) with `swap.amount_out` set equal to or greater than `total_pc_without_take_pnl`.
3. Execution reaches `Calculator::swap_token_amount_base_out` at [1](#0-0) , where `total_pc_without_take_pnl.checked_sub(amount_out)` returns `None`, and `.unwrap()` panics, aborting the transaction with an unhandled Rust panic instead of the designed `AmmError::InsufficientFunds` returned later at [6](#0-5) .

### Citations

**File:** program/src/math.rs (L335-364)
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

**File:** program/src/processor.rs (L2551-2556)
```rust
        let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(
            swap.amount_out.into(),
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        );
```

**File:** program/src/processor.rs (L2591-2595)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```
