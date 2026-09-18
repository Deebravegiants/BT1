Confirmed: in both `process_swap_base_out` and `process_swap_base_out_v2`, `Calculator::swap_token_amount_base_out` is invoked with the attacker-controlled `swap.amount_out` **before** any check that `swap.amount_out < total_pc_without_take_pnl` / `total_coin_without_take_pnl`. That bounds check only happens later, after the math and the transfer-amount computation.

### Title
Unvalidated `amount_out` causes reachable panic (`unwrap()` on `checked_sub`) in base-out swap math - ([File: program/src/math.rs])

### Summary
`Calculator::swap_token_amount_base_out` computes `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` (or the coin-side equivalent), and this function is called from `process_swap_base_out` / `process_swap_base_out_v2` with the raw, attacker-supplied `swap.amount_out` before the pool-reserve bound check (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) is performed later in the same function.

### Finding Description
`swap_token_amount_base_out` in [1](#0-0)  subtracts `amount_out` from the pool reserve using `checked_sub(amount_out).unwrap()`. If `amount_out >= total_pc_without_take_pnl` (Coin2PC) or `amount_out >= total_coin_without_take_pnl` (PC2Coin), `checked_sub` returns `None` and `.unwrap()` panics.

In `process_swap_base_out`, the call order is:
1. `swap_in_before_add_fee = Calculator::swap_token_amount_base_out(swap.amount_out.into(), total_pc_without_take_pnl.into(), total_coin_without_take_pnl.into(), swap_direction)` [2](#0-1) 
2. Only afterwards, deep inside the `match swap_direction` block, is the bound enforced: `if swap.amount_out >= total_pc_without_take_pnl { return Err(...) }` [3](#0-2)  / `if swap.amount_out >= total_coin_without_take_pnl { return Err(...) }` [4](#0-3) 

The identical ordering issue exists in `process_swap_base_out_v2`: the math call at [5](#0-4)  precedes the reserve checks at [6](#0-5) .

Since `swap.amount_out` is a raw `u64` field of `SwapInstructionBaseOut` fully controlled by the transaction sender's instruction data [7](#0-6) , and `total_pc_without_take_pnl`/`total_coin_without_take_pnl` are derived from the (attacker-chosen but real) pool's on-chain vault balances via `calc_total_without_take_pnl_no_orderbook` [8](#0-7) , any unprivileged caller can submit `amount_out` >= the relevant reserve to force a panic deep in the math helper before any graceful error path is reached. This is analogous to the CVE-2021-32494 bug class: an untrusted, attacker-controlled numeric input reaches an unchecked division/subtraction path and crashes program execution instead of returning a controlled error.

### Impact Explanation
A panic in a Solana on-chain program causes the transaction to abort with a runtime panic rather than a clean `ProgramError`. While the direct blast radius of a single failing transaction is limited to that transaction (it simply fails, and Solana's runtime does not persist a "crashed" program state), this defeats the program's own defensive-programming intent: the AMM already implements a specific `AmmError::InsufficientFunds` graceful-error path for this exact validation, and the panic path bypasses it. This is a robustness/availability regression for any composing on-chain program or off-chain integrator that relies on receiving a normal instruction error (e.g., simulated pre-flight checks, downstream CPI callers wrapping the swap) — a `panic!`/`unwrap` abort can produce different error surfaces/logs than intended and can be used to grief simulate-and-relay bots, or break composability of CPI callers that catch and interpret specific `ProgramError` codes rather than a generic panic. No direct fund theft or insolvency results because the transaction fails atomically before any token transfer occurs.

### Likelihood Explanation
High reachability: any signer can submit a `SwapBaseOut`/`SwapBaseOut_v2` instruction with attacker-chosen `amount_out` and valid (but otherwise ordinary) account bindings — no special privileges, leaked keys, or non-default builds are required. The only precondition is knowing (or guessing, since account data is public) the pool's current `total_pc_without_take_pnl` / `total_coin_without_take_pnl`, which are readable from public on-chain vault account balances, making the trigger trivially constructible in a single transaction.

### Recommendation
Reorder validation in `process_swap_base_out` and `process_swap_base_out_v2` so that `swap.amount_out < total_pc_without_take_pnl` (Coin2PC) / `swap.amount_out < total_coin_without_take_pnl` (PC2Coin) is checked and returns `AmmError::InsufficientFunds` **before** calling `Calculator::swap_token_amount_base_out`. Additionally, harden `swap_token_amount_base_out` itself to use `checked_sub(...).ok_or(AmmError::CheckedSubOverflow)?` (propagating a `Result`) instead of `.unwrap()`, so that any future caller cannot reintroduce the same reachable panic.

### Proof of Concept
1. Locate/create a Raydium AMM V4 pool (`AmmInfo`) with known vault balances, e.g. `total_pc_without_take_pnl = 1_000_000`, `total_coin_without_take_pnl = 500_000`.
2. Construct a `SwapInstructionBaseOut { amount_out: 1_000_000, max_amount_in: u64::MAX }` selecting `swap_direction = Coin2PC` (`user_source` mint = coin vault mint, `user_destination` mint = pc vault mint).
3. Submit the `SwapBaseOut` instruction (or `SwapBaseOut_v2`) in a single transaction with otherwise valid account bindings (correct PDAs, vault keys, signer).
4. Because `swap.amount_out (1_000_000) >= total_pc_without_take_pnl (1_000_000)`, `Calculator::swap_token_amount_base_out` executes `total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` → `checked_sub` returns `None` → `.unwrap()` panics, aborting the transaction with a runtime panic instead of the intended `AmmError::InsufficientFunds`, before the later explicit bound check at [3](#0-2)  is ever reached.

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

**File:** program/src/processor.rs (L2212-2216)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/processor.rs (L2236-2239)
```rust
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

**File:** program/src/processor.rs (L2591-2618)
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

**File:** program/src/instruction.rs (L91-99)
```rust
#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct SwapInstructionBaseIn {
    // SOURCE amount to transfer, output to DESTINATION is based on the exchange rate
    pub amount_in: u64,
    /// Minimum amount of DESTINATION token to output, prevents excessive slippage
    pub minimum_amount_out: u64,
}

```
