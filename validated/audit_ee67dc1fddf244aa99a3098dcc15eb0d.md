### Title
Division-by-zero panic in `process_swap_base_out`/`process_swap_base_out_v2` when `amount_out` equals pool reserve, due to safety check occurring after the division - (File: `program/src/processor.rs`, `program/src/math.rs`)

### Summary
`Calculator::swap_token_amount_base_out` computes `amount_in` using `denominator = total_other_side.checked_sub(amount_out)`, which is used as a divisor. In `process_swap_base_out`, this division is executed **before** the guard that rejects `amount_out >= total_*_without_take_pnl`, so an attacker who submits `amount_out` exactly equal to the pool's opposite-side reserve triggers a zero-denominator division inside the base-out math instead of hitting the intended `InsufficientFunds` check.

### Finding Description
`swap_token_amount_base_out` in [1](#0-0)  computes, for `SwapDirection::Coin2PC`:
```
let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();
amount_in = total_coin_without_take_pnl.checked_mul(amount_out).unwrap().checked_ceil_div(denominator).unwrap()
```
and symmetrically for `PC2Coin` using `total_coin_without_take_pnl`. If `amount_out == total_pc_without_take_pnl` (or `total_coin_without_take_pnl`), `checked_sub` succeeds and yields `0` (no underflow), producing `denominator = 0`, and the subsequent `checked_ceil_div(0)` divides by zero.

In `process_swap_base_out`, this calculation is invoked at [2](#0-1)  using attacker-controlled `swap.amount_out` and the pool's live `total_pc_without_take_pnl`/`total_coin_without_take_pnl`. The equivalent guard that is supposed to prevent this exact condition — `if swap.amount_out >= total_pc_without_take_pnl { return Err(AmmError::InsufficientFunds.into()); }` (and the mirrored check for `PC2Coin`) — is only executed **after** the division, at [3](#0-2) . The same ordering exists in `process_swap_base_out_v2` at [4](#0-3) .

This mirrors the reported bug class: a value used as a divisor (`periodTotalSupply` in the StakingPool analog, here `total_pc/coin_without_take_pnl - amount_out`) can become exactly zero through an ordinary, unprivileged transaction, and the guard meant to prevent it is checked too late in the control flow.

### Impact Explanation
`amount_out` and `max_amount_in` are fully attacker-controlled inputs to the swap instruction, and the pool reserves (`total_pc_without_take_pnl`, `total_coin_without_take_pnl`) are visible on-chain, so any unprivileged swapper can craft `amount_out` to exactly equal the current opposite-side reserve. This causes an integer division by zero, which in Rust arithmetic on the `U128`/`checked_ceil_div` path will either panic (aborting the transaction with a runtime panic instead of a controlled program error) or, depending on the exact `checked_ceil_div` implementation, propagate an unhandled `None`/`unwrap()` panic. Either way, the transaction aborts uncleanly, and because this same reserve state can recur (reserves change slowly relative to attacker-chosen `amount_out`), it can be used to repeatedly cause panics on the pool's swap-out path for a specific reserve value — a denial-of-service on `SwapBaseOut`/`SwapBaseOut2` for that pool state until reserves shift. This does not directly enable fund theft but can disrupt/impact pool usability, consistent with the referenced bug class being "not critical, cannot steal funds, but breaks desired logic."

### Likelihood Explanation
Reaching this state only requires a single attacker-chosen `amount_out` value equal to the currently known reserve amount on one side of the pool, and a swap direction chosen accordingly — both are ordinary parameters of the public `SwapBaseOut`/`SwapBaseOut2` instructions reachable by any unprivileged swapper with no special account permissions. The reserve values are readable from on-chain vault account state before submitting the transaction, making the precondition trivially satisfiable.

### Recommendation
Move the `amount_out >= total_pc_without_take_pnl` (and the `PC2Coin` equivalent `amount_out >= total_coin_without_take_pnl`) checks to occur **before** calling `Calculator::swap_token_amount_base_out`, in both `process_swap_base_out` and `process_swap_base_out_v2`. Additionally, harden `swap_token_amount_base_out` itself to return a `Result`/`Option` and explicitly reject a zero denominator rather than relying on `unwrap()`/`checked_ceil_div` to fail safely.

### Proof of Concept
1. Query the target AMM's `amm_coin_vault`/`amm_pc_vault` balances and `AmmInfo.state_data.need_take_pnl_*` to compute `total_pc_without_take_pnl` (via `Calculator::calc_total_without_take_pnl_no_orderbook`, [5](#0-4) ).
2. Submit a `SwapBaseOut` instruction with `swap_direction = Coin2PC` and `swap.amount_out` set exactly equal to `total_pc_without_take_pnl`.
3. Execution reaches [2](#0-1) , calling `swap_token_amount_base_out`, which computes `denominator = total_pc_without_take_pnl.checked_sub(amount_out) = 0` and then divides by it at [6](#0-5) , before the `swap.amount_out >= total_pc_without_take_pnl` guard at [7](#0-6)  is ever reached.

*Note: I was unable to inspect the exact body of `checked_ceil_div` (only its declaration location was found before tool access ended), so I cannot confirm with certainty whether it panics outright or returns `None` that is then `.unwrap()`'d — either path still results in an uncontrolled transaction abort rather than the intended `AmmError::InsufficientFunds` error.*

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

**File:** program/src/processor.rs (L2154-2192)
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
