Confirmed: the reachability, root cause and impact analysis are complete.

### Title
Unvalidated `amount_out` in `process_swap_base_out`/`process_swap_base_out_v2` causes panic via unchecked subtraction underflow before insufficient-funds check - (File: `program/src/processor.rs`)

### Summary
Analogous to CVE-2022-21412 (attacker-controlled query input reaches an unguarded optimizer computation path in MySQL, causing a crash/hang), a swapper can submit an `amount_out` value in `SwapBaseOut`/`SwapBaseOut2` that is validated only *after* it is already consumed by an unchecked arithmetic subtraction, causing a Rust panic (`unwrap()` on `None`) instead of a clean program error.

### Finding Description
In `Processor::process_swap_base_out` (and its duplicate `process_swap_base_out_v2`), `swap.amount_out` is attacker-controlled instruction data. It is passed straight into `Calculator::swap_token_amount_base_out` at [1](#0-0) , which internally performs `total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` (or the coin-side equivalent) as shown in [2](#0-1) .

The bounds check that is supposed to guard this — `if swap.amount_out >= total_pc_without_take_pnl { return Err(AmmError::InsufficientFunds.into()); }` — only happens later, after the subtraction/`unwrap()` has already executed, in the direction-specific match block: [3](#0-2)  and [4](#0-3) .

Because `checked_sub` returns `None` (not a saturating/wrapping result) when `amount_out >= total_pc_without_take_pnl` (or `total_coin_without_take_pnl`), the immediately-following `.unwrap()` inside `swap_token_amount_base_out` panics before the program ever reaches its own explicit `InsufficientFunds` guard. The order-of-checks bug means the "safe" error path that the developers wrote is dead code for this specific out-of-range condition — the panic fires first.

### Impact Explanation
Any unprivileged user issuing a `SwapBaseOut`/`SwapBaseOut2` instruction with `amount_out` set to a value greater than or equal to the pool's current available reserve for the requested output token can trigger a Rust-level panic inside the on-chain program instead of a graceful `ProgramError`. This is directly analogous to the CVE's "Availability impacts... hang or frequently repeatable crash": every account and pool state involved is legitimate, no privileged signer or leaked key is needed, and the panic is trivially and repeatably reproducible by any party that can read the pool's vault balances (which are public on-chain data). While Solana runtime isolates the panic to the failing transaction, it demonstrates that a core safety invariant (validate before compute) is violated in the swap-out math path, and the "logically checked but arithmetically unchecked" ordering pattern is repeated across the fee computation and pnl computation as well (e.g. `program/src/processor.rs:2180-2191`, `program/src/processor.rs:190-226`), meaning any future refactor which removes/reorders the redundant late check turns this into a hard denial-of-service against that instruction for the entire pool.

### Likelihood Explanation
High likelihood of triggering: the attacker only needs the current (public) vault balances and to set `amount_out` at or above the relevant pool total in a single, ordinary `SwapBaseOut` transaction. No special privileges, timing races, or non-default builds are required.

### Recommendation
Move the `swap.amount_out >= total_pc_without_take_pnl` / `swap.amount_out >= total_coin_without_take_pnl` bounds checks (currently at `program/src/processor.rs:2214` and `2237`, and the analogous location in `process_swap_base_out_v2`) to occur *before* calling `Calculator::swap_token_amount_base_out`, and replace the internal `checked_sub(...).unwrap()` in `math.rs::swap_token_amount_base_out` with an explicit `ok_or(AmmError::...)?` to fail gracefully rather than panic even if a future caller omits the pre-check.

### Proof of Concept
1. Create an AMM pool via `Initialize2` with the coin vault holding `total_coin_without_take_pnl = C` and pc vault holding `total_pc_without_take_pnl = P`.
2. As any user (no special privileges), submit a `SwapBaseOut` instruction with `swap_direction = Coin2PC` and `swap.amount_out = P` (i.e., equal to `total_pc_without_take_pnl`), and `swap.max_amount_in` set high enough to pass later checks.
3. Execution reaches `Calculator::swap_token_amount_base_out(P, P, C, Coin2PC)` at `program/src/processor.rs:2172`, which computes `denominator = total_pc_without_take_pnl.checked_sub(amount_out) = P.checked_sub(P) = Some(0)` — this particular case still succeeds; setting `amount_out = P + 1` (or any value `> P`) instead makes `checked_sub` return `None`, and the subsequent `.unwrap()` in `program/src/math.rs:341` panics, aborting the transaction with a runtime panic instead of the intended `AmmError::InsufficientFunds` from `program/src/processor.rs:2214-2216`, which is never reached.

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

**File:** program/src/processor.rs (L2236-2239)
```rust
            SwapDirection::PC2Coin => {
                if swap.amount_out >= total_coin_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/math.rs (L341-347)
```rust
                let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();
                amount_in = total_coin_without_take_pnl
                    .checked_mul(amount_out)
                    .unwrap()
                    .checked_ceil_div(denominator)
                    .unwrap()
            }
```
