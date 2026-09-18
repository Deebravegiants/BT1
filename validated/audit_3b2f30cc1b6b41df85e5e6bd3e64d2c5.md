This confirms the vulnerable pattern: both `process_swap_base_out` and `process_swap_base_out_v2` call `Calculator::swap_token_amount_base_out` with the raw, unvalidated `swap.amount_out` **before** any check that `swap.amount_out < total_pc_without_take_pnl` (or `total_coin_without_take_pnl`). That range check only happens later, inside the `match swap_direction` block, after the division has already executed and after fund transfers are about to occur.

Inside `swap_token_amount_base_out` (`program/src/math.rs:327-367`), the denominator is computed via an unchecked-order subtraction:
```
let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();
```
(or `total_coin_without_take_pnl.checked_sub(amount_out).unwrap()` for the other direction). If the attacker-supplied `amount_out` is `>=` the pool's available balance, `checked_sub` returns `None` and `.unwrap()` panics, aborting the transaction — this is a direct analog of the CVE's root cause: the relationship between two length/amount values (`p->rem`/`p->len` in openrsync vs. `amount_out`/`total_..._without_take_pnl` here) is used in a subtraction before it is validated. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Unchecked subtraction order in `swap_token_amount_base_out` allows an unprivileged swapper to panic the program via SwapBaseOut/SwapBaseOutV2 - ([File: program/src/math.rs])

### Summary
`process_swap_base_out` and `process_swap_base_out_v2` invoke `Calculator::swap_token_amount_base_out` with the caller-supplied `swap.amount_out` before validating that `amount_out` is less than the pool's available reserve for the requested output token. The validation (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) is performed afterward, inside the direction-specific transfer branch, so it never protects the earlier arithmetic.

### Finding Description
In `swap_token_amount_base_out` (`program/src/math.rs:327-367`), for the `Coin2PC` direction the code computes:
```rust
let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();
```
and for `PC2Coin`:
```rust
let denominator = total_coin_without_take_pnl.checked_sub(amount_out).unwrap();
```
Both call sites in `process_swap_base_out` (`program/src/processor.rs:2172-2177`) and `process_swap_base_out_v2` (`program/src/processor.rs:2551-2556`) pass the raw instruction field `swap.amount_out` — fully attacker-controlled — as `amount_out`, and the pool reserve values `total_pc_without_take_pnl`/`total_coin_without_take_pnl` are derived from live vault balances. No prior check bounds `swap.amount_out` relative to these reserves. The bound check (`swap.amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl`) only executes later at lines 2214/2237 (and the analogous lines in the `_v2` variant), i.e., after `swap_token_amount_base_out` has already run.

If `swap.amount_out` is chosen to be greater than or equal to the pool's available reserve for the token being withdrawn, `checked_sub` returns `None`, and the immediate `.unwrap()` panics, aborting the transaction with a runtime panic. This mirrors the openrsync CVE's root cause: a length/amount relationship (`p->rem` vs `p->len` there; `amount_out` vs pool reserve here) is consumed by a subtraction/arithmetic routine without first checking that the relationship is even valid, letting a remote/unprivileged party trigger a crash purely through crafted instruction data.

### Impact Explanation
Any unprivileged user can submit a single `SwapBaseOut` or `SwapBaseOutV2` transaction with attacker-chosen `amount_out` (and arbitrary token/account selection consistent with mint checks) to force a program panic on any live pool. While a Solana program panic only aborts the single transaction (not a process-wide SIGSEGV as in the native openrsync case), it is a reliable, cheaply repeatable denial-of-service primitive against a specific pool/instruction path, and indicates a broader pattern of validating attacker-controlled amounts too late relative to the arithmetic that consumes them.

### Likelihood Explanation
High likelihood of exploitability: the attacker fully controls `swap.amount_out` via instruction data (`program/src/instruction.rs:426-433`), needs no special privileges or signer roles beyond being a normal swap initiator, and the reserve values are observable on-chain, making it trivial to pick an `amount_out` that satisfies `amount_out >= total_..._without_take_pnl`.

### Recommendation
Move the reserve-sufficiency checks (`swap.amount_out < total_pc_without_take_pnl` for `Coin2PC`, `swap.amount_out < total_coin_without_take_pnl` for `PC2Coin`) to occur before calling `Calculator::swap_token_amount_base_out`, in both `process_swap_base_out` and `process_swap_base_out_v2`. Additionally, harden `swap_token_amount_base_out` itself to return a proper `AmmError` (e.g., `AmmError::InsufficientFunds`) instead of `.unwrap()`-ing the `checked_sub` result, so the invariant is enforced at the math layer regardless of caller ordering.

### Proof of Concept
1. Attacker identifies a live pool and reads its current `amm_pc_vault`/`amm_coin_vault` balances to determine `total_pc_without_take_pnl` (via `calc_total_without_take_pnl_no_orderbook`).
2. Attacker submits a `SwapBaseOut` (opcode 11) instruction with `amount_out` set to a value `>= total_pc_without_take_pnl` (for the `Coin2PC` direction) and any `max_amount_in`.
3. Inside `process_swap_base_out`, execution reaches `Calculator::swap_token_amount_base_out(swap.amount_out.into(), total_pc_without_take_pnl.into(), ..., SwapDirection::Coin2PC)` at `program/src/processor.rs:2172-2177`.
4. Inside `swap_token_amount_base_out`, `total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` at `program/src/math.rs:341` receives `None` and panics, aborting the transaction — reachable purely from a single unprivileged transaction with attacker-chosen instruction data.

### Citations

**File:** program/src/math.rs (L327-346)
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
```

**File:** program/src/processor.rs (L2172-2216)
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
        encode_ray_log(SwapBaseOutLog {
            log_type: LogType::SwapBaseOut.into_u8(),
            max_in: swap.max_amount_in,
            amount_out: swap.amount_out,
            direction: swap_direction as u64,
            user_source: user_source.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            deduct_in: swap_in_after_add_fee,
        });
        if user_source.amount < swap_in_after_add_fee {
            return Err(AmmError::InsufficientFunds.into());
        }
        if swap.max_amount_in < swap_in_after_add_fee {
            return Err(AmmError::ExceededSlippage.into());
        }
        if swap_in_after_add_fee == 0 || swap.amount_out == 0 {
            return Err(AmmError::InvalidInput.into());
        }

        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/processor.rs (L2551-2587)
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
        encode_ray_log(SwapBaseOutLog {
            log_type: LogType::SwapBaseOut.into_u8(),
            max_in: swap.max_amount_in,
            amount_out: swap.amount_out,
            direction: swap_direction as u64,
            user_source: user_source.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            deduct_in: swap_in_after_add_fee,
        });
        if user_source.amount < swap_in_after_add_fee {
            return Err(AmmError::InsufficientFunds.into());
        }
        if swap.max_amount_in < swap_in_after_add_fee {
            return Err(AmmError::ExceededSlippage.into());
        }
        if swap_in_after_add_fee == 0 || swap.amount_out == 0 {
```
