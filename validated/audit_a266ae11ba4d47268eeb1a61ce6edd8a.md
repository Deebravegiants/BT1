### Title
Integer truncation in `swap_token_amount_base_out` → `as_u64()` allows near-total drain of a swap vault via `SwapBaseOut`/`SwapBaseOutV2` - (`program/src/processor.rs`)

### Summary
`swap_base_out` and `swap_base_out_v2` compute the required input amount in wide `U128` arithmetic and then convert it to `u64` with a raw `.as_u64()` call instead of a checked conversion, mirroring the integer-truncation bug class in CVE-2018-8786 (a wide computed value silently truncated to a narrower type and then trusted for a security-critical downstream operation).

### Finding Description
`Calculator::swap_token_amount_base_out` computes, for `SwapDirection::Coin2PC`:
`amount_in = coin * amount_out / (pc - amount_out)` entirely in `U128`. [1](#0-0) 

If the attacker (an unprivileged swapper who fully controls `swap.amount_out` and `swap.max_amount_in` in the instruction data) chooses `amount_out` just below `total_pc_without_take_pnl`, the denominator `pc - amount_out` becomes very small (e.g., 1), making `amount_in` balloon to a value far larger than `u64::MAX` while still safely fitting in `U128` (since `u64::MAX^2 < U128::MAX`), so none of the `checked_mul`/`checked_ceil_div` calls panic.

That oversized `U128` value is then narrowed with a bare `.as_u64()` (no `try_into`/checked path), unlike the safe `Calculator::to_u64` helper used elsewhere in the file: [2](#0-1) [3](#0-2) 

The `uint` crate's `as_u64()` on a value whose bit-length exceeds 64 either truncates to the low 64 bits or panics depending on build/debug-assertion configuration; Solana BPF programs are built in release mode, so debug assertions used by some `uint` versions for this check are compiled out, and the truncated (effectively attacker-influenced, small) value is used as `swap_in_after_add_fee`. All subsequent guard checks operate on this already-truncated value: [4](#0-3) 
and the vault-sufficiency check only bounds `swap.amount_out`, not the truncated input, before executing the CPIs: [5](#0-4) 

Because `swap_in_after_add_fee` is truncated to a small/attacker-influenced number, the attacker can satisfy `user_source.amount < swap_in_after_add_fee` and `swap.max_amount_in < swap_in_after_add_fee` trivially, then have the program transfer only that tiny truncated amount into the vault while transferring nearly all of `total_pc_without_take_pnl` (the attacker-chosen `swap.amount_out`) back out via `Invokers::token_transfer` / `Invokers::token_transfer_with_authority`.

### Impact Explanation
If exploitable as analyzed, this allows an unprivileged swapper to drain a pool's `pc` (or `coin`) vault for a negligible real payment by exploiting the truncation, resulting in concrete theft of LP/pool funds and insolvent pool accounting — a critical impact class matching the "theft or permanent freezing of user or LP funds / insolvent pool accounting" bar in the validation rules.

### Likelihood Explanation
The path is reachable from a single transaction (`SwapBaseOut`/`SwapBaseOutV2` instruction) with fully attacker-controlled `amount_out` and `max_amount_in`, no privileged signer required, and standard SPL token accounts. However, I was **unable to conclusively verify** the exact runtime behavior of `uint`'s `as_u64()` in this crate's pinned version (0.10.0) — whether it truncates silently or panics — because I could not fetch the crate source through available tools; only `Cargo.lock` metadata was retrievable, not the vendored/crates.io source of `uint 0.10.0`. If `as_u64()` panics on overflow (many `uint` crate versions do, even outside `debug_assertions`), this becomes a transaction-abort/DoS rather than a silent-truncation fund-theft bug, which would fall outside the "no-impact" exclusion in the rules. This uncertainty is the primary caveat on this finding.

### Recommendation
Replace the bare `.as_u64()` calls at the `swap_in_after_add_fee` computation sites in both `swap_base_out` and `swap_base_out_v2` with a checked conversion (e.g., `Calculator::to_u64(...)` pattern already used elsewhere, or `u64::try_from(...)` returning `AmmError::ConversionFailure` on failure), and add an explicit bound checking `amount_out < total_pc_without_take_pnl` (or coin equivalent) with sufficient margin before performing the division, so the denominator can never shrink enough to produce a value outside `u64` range.

### Proof of Concept
Conceptual sequence (requires confirming `uint::as_u64()` truncation behavior in this build, per the caveat above):
1. Attacker creates/uses a pool with a nonzero `pc` vault balance `P` (`total_pc_without_take_pnl`).
2. Attacker submits `SwapBaseOut` with `swap.amount_out = P - 1` and `swap.max_amount_in` set to a small value equal to the expected truncated result, `user_source` token account funded with that small amount.
3. `Calculator::swap_token_amount_base_out` computes `amount_in = coin * (P-1) / 1`, an astronomically large `U128` value. [6](#0-5) 
4. `.as_u64()` truncates this to a small value [7](#0-6) , passing the `user_source.amount < swap_in_after_add_fee` and `max_amount_in` checks trivially [4](#0-3) .
5. The program transfers only the truncated (tiny) amount into the vault but pays out `P - 1` to the attacker [8](#0-7) , draining nearly the entire `pc` vault.

### Citations

**File:** program/src/math.rs (L327-347)
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

**File:** program/src/processor.rs (L2202-2210)
```rust
        if user_source.amount < swap_in_after_add_fee {
            return Err(AmmError::InsufficientFunds.into());
        }
        if swap.max_amount_in < swap_in_after_add_fee {
            return Err(AmmError::ExceededSlippage.into());
        }
        if swap_in_after_add_fee == 0 || swap.amount_out == 0 {
            return Err(AmmError::InvalidInput.into());
        }
```

**File:** program/src/processor.rs (L2212-2234)
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
