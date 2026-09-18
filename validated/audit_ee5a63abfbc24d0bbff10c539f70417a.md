### Title
Unchecked `U128` → `u64` truncation in `swap_token_amount_base_out` allows attacker to drain pool while paying a near-zero, wrapped-around input amount - ([File: program/src/math.rs], [File: program/src/processor.rs])

### Summary
The reported Tokensoft bug is a classic unsafe/unchecked narrowing cast (`uint256`→`uint120`) that silently truncates a value that should have been bounds-checked before downcast, letting the check that is supposed to reject an oversized value operate on the already-truncated number instead of the original one. Raydium's swap-exact-out path (`SwapBaseOut` / `SwapBaseOut2`) has the same class of bug: `Calculator::swap_token_amount_base_out` (`program/src/math.rs:327-367`) computes the required input amount entirely in `U128`, and the caller then narrows that `U128` result to `u64` with `.as_u64()` (`program/src/processor.rs:2191` and `program/src/processor.rs:2570`). The `U128`/`U256` types are produced by the `uint` crate's `construct_uint!` macro (`program/src/math.rs:9-16`), whose `as_u64()` method truncates to the low 64 bits without any overflow check or panic — it is not a checked/`try_into` conversion like `Calculator::to_u64` (`program/src/math.rs:46-48`) uses elsewhere.

### Finding Description
In the base-out swap math:
```
program/src/math.rs:341-346  (Coin2PC)
let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();
amount_in = total_coin_without_take_pnl.checked_mul(amount_out).unwrap().checked_ceil_div(denominator).unwrap()
``` [1](#0-0) 

As `amount_out` approaches the pool's actual reserve (`total_pc_without_take_pnl`), `denominator` shrinks toward `1`, while the numerator `total_coin_without_take_pnl * amount_out` can be as large as the product of two near-`u64::MAX` reserve values (which fits in `U128`, since `(2^64-1)^2 < 2^128-1`). The quotient `amount_in` can therefore legitimately be far larger than `u64::MAX` while still fitting comfortably inside `U128`.

That oversized `U128` result then flows into:
```
program/src/processor.rs:2172-2191
let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(...);
let swap_in_after_add_fee = swap_in_before_add_fee
    .checked_mul(amm.fees.swap_fee_denominator.into()).unwrap()
    .checked_ceil_div(...).unwrap()
    .as_u64();
``` [2](#0-1) 
and the identical pattern in the second swap-out entrypoint: [3](#0-2) 

`.as_u64()` on the `uint` crate's `U128` type (defined via `construct_uint!` at `program/src/math.rs:9-16`) truncates to the low 64 bits with no panic and no error return, unlike the codebase's own safe helper `Calculator::to_u64` which uses `try_into()` and returns `AmmError::ConversionFailure` on overflow (`program/src/math.rs:46-48`). Because the fee-scaling multiplication (`checked_mul`) is checked against `U128::MAX` (not `u64::MAX`), a value that is enormous in `u64` terms but still under `2^128` sails through the `unwrap()` without panicking, and only the final `.as_u64()` silently wraps it down to a small, essentially attacker-influenced residue.

The truncated `swap_in_after_add_fee` is then used as the amount the swapper must actually pay:
```
program/src/processor.rs:2581
if user_source.amount < swap_in_after_add_fee { ... InsufficientFunds }
``` [4](#0-3) 

Since this check (and the transfer amount used later) is performed on the wrapped/truncated value, the swap succeeds with the attacker transferring only the tiny truncated amount into the pool while receiving `swap.amount_out` (potentially almost the entire pool reserve) out of the vault, exactly analogous to the referenced report where the downstream `require` validated the already-downcast (and thus meaningless) quantity instead of the true, pre-cast value.

### Impact Explanation
This allows an attacker to withdraw close to the entire pool reserve of one side while paying only a wrapped-around (effectively attacker-influenced, potentially near-zero) `u64` amount on the other side, directly draining LP/pool funds — this is concrete theft of user/LP funds and insolvent pool accounting, matching the required severity bar (Medium/High/Critical, concrete fund theft).

### Likelihood Explanation
The vulnerable computation is reachable from a single `SwapBaseOut`/`SwapBaseOut2` transaction submitted by any unprivileged swapper with attacker-chosen `amount_out` (`program/src/processor.rs:2154-2192`, `program/src/processor.rs:2551-2570`), which is one of the explicitly in-scope swap instructions. Triggering the overflow requires the pool's coin/pc reserves and the chosen `amount_out` to be large enough (close to `u64::MAX`-scale token amounts, e.g. via a pool created with a high-supply/high-decimal SPL token, an action a pool creator can freely perform), which is plausible but requires specific reserve magnitudes rather than being triggerable against every pool trivially — hence a real but reserve-size-dependent likelihood.

### Recommendation
Replace all direct `.as_u64()` truncations on `U128`/`U256` results derived from `swap_token_amount_base_out` (and any other unchecked `.as_u64()` calls fed by attacker-influenced multiplication/division chains) with the existing safe helper `Calculator::to_u64`, which uses `try_into()` and propagates `AmmError::ConversionFailure` instead of silently wrapping. Additionally, validate that `amount_in`/`swap_in_after_add_fee` never exceeds `u64::MAX` before using it in downstream comparisons and token transfers.

### Proof of Concept
1. An unprivileged user calls `Initialize2` to create a pool for a custom SPL token minted with the maximum practical supply/decimals so the coin (or pc) vault balance is close to `u64::MAX`.
2. A swapper calls `SwapBaseOut` (or `SwapBaseOut2`) with `amount_out` chosen so that `total_pc_without_take_pnl - amount_out` (the `denominator` in `swap_token_amount_base_out`, `program/src/math.rs:341`) is minimal (e.g., `1`), forcing `amount_in = total_coin_without_take_pnl * amount_out / denominator` to be a `U128` value far exceeding `u64::MAX` but still under `U128::MAX`.
3. `swap_in_before_add_fee.checked_mul(fee_denominator).checked_ceil_div(...)` stays within `U128` bounds (no panic) but produces a result still > `u64::MAX`.
4. `.as_u64()` (`program/src/processor.rs:2191`/`2570`) truncates this to the low 64 bits, yielding a small wrapped value used for the `user_source.amount < swap_in_after_add_fee` check (`program/src/processor.rs:2581`) and for the actual token transfer amount.
5. The swapper transfers only the truncated (small) amount into the pool vault yet receives the requested `amount_out` (near the full reserve) from the other vault, draining the pool.

### Citations

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

**File:** program/src/processor.rs (L2581-2581)
```rust
        if user_source.amount < swap_in_after_add_fee {
```
