Confirmed. This gives a solid, reachable analog to the CVE-2017-12782 "assert fault on crafted input" bug class — a checked-arithmetic panic (`unwrap()`) triggered before any bounds validation, on attacker-controlled instruction data. Since `swap.amount_out` is fully attacker-controlled and `swap_token_amount_base_out` is invoked at line 2172 (in `process_swap_base_out`) — before the `swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl` guard that appears only later at lines 2214/2237 — an unprivileged swapper can submit a single `SwapBaseOut` transaction with `amount_out` at or above the pool's available liquidity to force `checked_sub(amount_out).unwrap()` to underflow and panic.

### Title
Unvalidated `amount_out` causes unchecked-subtraction panic (DoS) in `process_swap_base_out` before liquidity bounds check - (File: program/src/processor.rs, program/src/math.rs)

### Summary
`process_swap_base_out` (and its V2 counterpart) calls `Calculator::swap_token_amount_base_out` with the caller-supplied `swap.amount_out` before validating that `amount_out` is smaller than the pool's available liquidity (`total_pc_without_take_pnl` / `total_coin_without_take_pnl`). Inside that function, `denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` (or the coin-side equivalent) will return `None` and panic whenever `amount_out` is greater than or equal to the pool reserve, because the compensating liquidity check only happens afterward.

### Finding Description
`process_swap_base_out` unpacks `swap.amount_out` directly from unpacked instruction data [1](#0-0) , then computes pool reserves and calls `Calculator::swap_token_amount_base_out` at [2](#0-1) . Inside `swap_token_amount_base_out`, the denominator for both swap directions is computed via unchecked-then-`unwrap()`ed subtraction of `amount_out` from the pool's total reserve [3](#0-2) . The corresponding safety check that would reject an `amount_out` at or beyond the pool reserve (`if swap.amount_out >= total_pc_without_take_pnl { return Err(...) }`) only executes after this calculation, inside the `match swap_direction` block at [4](#0-3)  and [5](#0-4) . The identical ordering issue exists in `process_swap_base_out_v2` [6](#0-5) . This is the direct analog to CVE-2017-12782's pattern of an assert/unwrap fault triggered by unvalidated, attacker-supplied data reaching an internal invariant check before input sanitation.

### Impact Explanation
Because `checked_sub(...).unwrap()` panics rather than returning a `ProgramError`, the transaction aborts via a runtime panic instead of a controlled instruction error. Any unprivileged user can submit a `SwapBaseOut`/`SwapBaseOutV2` instruction with attacker-chosen accounts (any valid pool) and `amount_out` set to be greater than or equal to the current pool-side reserve to trigger this panic on demand — a denial-of-service condition reachable from a single transaction. While the transaction itself is reverted by the Solana runtime (no direct fund loss on that call), this is a reachable, unguarded panic path in core swap logic that a malicious actor fully controls, satisfying the CVE's bug class of "denial of service via crafted/attacker-controlled input triggering an internal assert/unwrap fault" rather than a graceful, intended error.

### Likelihood Explanation
High: the only requirements are a valid pool (any AMM pool, including one the attacker creates via `Initialize2`) and setting `amount_out` in the instruction data to any value at or above the pool's real-time reserve for the requested output side. No privileged signer, special build, or off-chain component is required — a single, ordinary submitted transaction with attacker-chosen `amount_out` reaches the vulnerable path deterministically.

### Recommendation
Move the liquidity-sufficiency checks (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) in both `process_swap_base_out` and `process_swap_base_out_v2` to occur before calling `Calculator::swap_token_amount_base_out`, and replace the `unwrap()` calls in `swap_token_amount_base_out`'s `checked_sub` with explicit error returns (e.g., `ok_or(AmmError::CalculationExRateFailure)?`) so that out-of-range `amount_out` values always produce a controlled `ProgramError` instead of a panic.

### Proof of Concept
1. Create or select any live Raydium AMM pool with known reserves, e.g. `total_pc_without_take_pnl = P`.
2. Submit a `SwapBaseOut` (tag `11`) instruction, direction Coin2PC, with `amount_out = P` (or any value `>= P`) and arbitrary `max_amount_in`.
3. `process_swap_base_out` reaches [2](#0-1)  before the sufficiency check, calling into `swap_token_amount_base_out`.
4. `total_pc_without_take_pnl.checked_sub(amount_out)` evaluates to `None` (since `amount_out >= total_pc_without_take_pnl`), and `.unwrap()` at [7](#0-6)  panics, aborting the instruction with an uncontrolled runtime panic instead of the intended `AmmError::InsufficientFunds`.

### Citations

**File:** program/src/instruction.rs (L426-432)
```rust
            11 => {
                let (max_amount_in, rest) = Self::unpack_u64(rest)?;
                let (amount_out, _rest) = Self::unpack_u64(rest)?;
                Self::SwapBaseOut(SwapInstructionBaseOut {
                    max_amount_in,
                    amount_out,
                })
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

**File:** program/src/math.rs (L335-346)
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
```
