Confirmed. In `Calculator::swap_token_amount_base_out` (`program/src/math.rs:327-367`), the denominator is computed as `total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` (Coin2PC) or `total_coin_without_take_pnl.checked_sub(amount_out).unwrap()` (PC2Coin), where `amount_out` comes directly from the attacker-supplied `swap.amount_out` instruction field. In both `process_swap_base_out` and `process_swap_base_out_v2` (`program/src/processor.rs:2172-2177` and `2551-2556`), this function is called *before* the sufficiency check `if swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl` that only occurs later at lines 2214/2593 (inside the `match swap_direction` block). This ordering issue is the exploitable analog. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Unchecked `checked_sub().unwrap()` panic on attacker-controlled `amount_out` in SwapBaseOut before validation - (File: program/src/math.rs / program/src/processor.rs)

### Summary
`process_swap_base_out` and `process_swap_base_out_v2` compute the required input amount by calling `Calculator::swap_token_amount_base_out` with the raw, unvalidated `swap.amount_out` field from the instruction data, before the pool-liquidity sufficiency check (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) is performed. Inside that function, the denominator is `total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` (or the coin equivalent), which panics whenever `amount_out` is greater than or equal to the pool's available reserve, since `checked_sub` returns `None` on underflow and `.unwrap()` aborts the program.

### Finding Description
Any unprivileged user submitting a `SwapBaseOut` (opcode 11) or `SwapBaseOutV2` transaction fully controls the `amount_out` field via `AmmInstruction::unpack` [4](#0-3) . The processor reads live vault balances, derives `total_pc_without_take_pnl`/`total_coin_without_take_pnl`, and immediately calls `Calculator::swap_token_amount_base_out(swap.amount_out.into(), ...)` [2](#0-1)  — well before the later guard at line 2593/2214 that would reject an over-large `amount_out`. Inside `swap_token_amount_base_out`, both branches perform `checked_sub(amount_out).unwrap()` on the pool total [5](#0-4) . Because `amount_out` is attacker-chosen and can trivially exceed the pool's reserve (e.g. `u64::MAX`), the subtraction underflows, `checked_sub` yields `None`, and `.unwrap()` triggers a Rust panic, aborting the on-chain program execution for that instruction. This mirrors the CVE-2021-32815 bug class: a crafted, attacker-supplied input reaching an unguarded assertion/panic path that a downstream consumer relies on for normal operation, causing a forced abort instead of a controlled error path.

### Impact Explanation
The panic causes the entire transaction (and, if invoked from a downstream integrator's on-chain program via CPI, the caller's transaction as well) to abort ungracefully instead of returning a normal `ProgramError`. Any composing on-chain program or aggregator that depends on Raydium's swap instruction returning a typed `Err` (as the sibling checks elsewhere in the file do, e.g. `AmmError::InsufficientFunds`) instead gets an unrecoverable panic, which can break assumptions in wrapping instructions/transactions and is directly reachable by any unprivileged swapper with a single crafted instruction against any live AMM pool.

### Likelihood Explanation
Trivial to trigger: no special privileges, accounts, or preconditions are needed beyond a valid `AmmInfo`/vault set and a `SwapBaseOut`/`SwapBaseOutV2` instruction with `amount_out` set larger than the current pool reserve of the output token — a condition attackers fully control and can hit on the very first call.

### Recommendation
Reorder the checks so the sufficiency validation (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) happens before calling `Calculator::swap_token_amount_base_out`, and/or change `swap_token_amount_base_out` to return a `Result`/`Option` via `checked_sub().ok_or(AmmError::...)?` instead of `.unwrap()`, consistent with the pattern already used in `calc_total_without_take_pnl_no_orderbook` [6](#0-5) .

### Proof of Concept
1. Identify any live Raydium AMM pool and read its `amm_pc_vault`/`amm_coin_vault` balances and `need_take_pnl_pc`/`need_take_pnl_coin` to know `total_pc_without_take_pnl`.
2. Submit a `SwapBaseOut` instruction (tag `11`) with `amount_out` set to a value ≥ `total_pc_without_take_pnl` (e.g. `u64::MAX`), valid signer/vault accounts, and any `max_amount_in`.
3. `process_swap_base_out` computes `swap_in_before_add_fee = Calculator::swap_token_amount_base_out(...)` before the sufficiency check; inside, `total_pc_without_take_pnl.checked_sub(amount_out)` underflows and `.unwrap()` panics, aborting the transaction instead of returning `AmmError::InsufficientFunds`.

### Citations

**File:** program/src/math.rs (L243-248)
```rust
        let total_pc_without_take_pnl = pc_amount
            .checked_sub(amm.state_data.need_take_pnl_pc)
            .ok_or(AmmError::CheckedSubOverflow)?;
        let total_coin_without_take_pnl = coin_amount
            .checked_sub(amm.state_data.need_take_pnl_coin)
            .ok_or(AmmError::CheckedSubOverflow)?;
```

**File:** program/src/math.rs (L341-358)
```rust
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

**File:** program/src/processor.rs (L2591-2595)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/instruction.rs (L426-431)
```rust
            11 => {
                let (max_amount_in, rest) = Self::unpack_u64(rest)?;
                let (amount_out, _rest) = Self::unpack_u64(rest)?;
                Self::SwapBaseOut(SwapInstructionBaseOut {
                    max_amount_in,
                    amount_out,
```
