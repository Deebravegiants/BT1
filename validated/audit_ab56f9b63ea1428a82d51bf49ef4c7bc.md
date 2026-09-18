### Title
Withdraw can be permanently blocked by a rounding-to-zero check on derived `coin_amount`/`pc_amount` when reserves shrink relative to `lp_amount`, freezing LP holders' funds - ([File: program/src/processor.rs])

### Summary
`process_withdraw` reverts whenever the *computed* proportional `coin_amount` or `pc_amount` rounds down to zero, even though the caller's `withdraw.amount` of LP tokens is non-zero and represents a real, non-zero claim on the pool. Combined with the pool's ban on ever withdrawing 100% of `amm.lp_amount` in one call, this can make it mathematically impossible for a real LP holder to ever withdraw once one side of the pool's `*_without_take_pnl` reserve becomes small relative to `amm.lp_amount` — exactly the same bug class as the referenced report (a check performed on a *derived* value rather than on the actual user entitlement/config, causing an unlock/withdraw that should succeed to always revert).

### Finding Description
In `process_withdraw`, the amount of LP tokens the caller may burn is first bounded away from the total supply: [1](#0-0) 

so a caller can never redeem the *last* unit of `amm.lp_amount` — some `amm.lp_amount` must always remain outstanding after any single withdraw call.

Then the actual token amounts returned to the user are computed proportionally from the current (pnl-adjusted) reserves: [2](#0-1) 

and afterward the instruction unconditionally reverts if either side rounds to zero: [3](#0-2) 

`total_pc_without_take_pnl` / `total_coin_without_take_pnl` are not fixed values — they shrink whenever the pool owner calls `process_withdrawpnl` to sweep out `need_take_pnl_coin`/`need_take_pnl_pc`, and are also reduced every time `calc_take_pnl` recalculates PnL relative to `target_orders.calc_pnl_x/y`: [4](#0-3) [5](#0-4) 

If, for a given token side, `total_*_without_take_pnl` becomes small relative to `amm.lp_amount` (e.g., after repeated PnL extraction, decimal disparities between coin/pc, or a pool that is heavily skewed to one side), then for **any** `withdraw.amount` a normal LP holder can legally submit (i.e. `withdraw.amount < amm.lp_amount`, since the max is capped below `amm.lp_amount`), the floor-division `exchange_pool_to_token` on that side will round to `0`. The `withdraw.amount == 0 || coin_amount == 0 || pc_amount == 0` check then rejects the transaction outright with `AmmError::InvalidInput`, regardless of how large `withdraw.amount` (up to just under `amm.lp_amount`) is. Because the "always leave at least 1 unit of `lp_amount` outstanding" rule prevents ever draining the pool completely, and the zero-round-down check independently vetoes any partial withdrawal whose proportional share underflows to zero on either token side, LP holders holding a real, non-zero claim on the pool can be locked out of `Withdraw` entirely — this is the same root-cause pattern as the report: a revert gated on a *derived quantity* (`getTotalUnits`/here, rounded `coin_amount`/`pc_amount`) rather than on whether the user's actual claim is legitimately zero.

### Impact Explanation
This results in permanent freezing of LP holders' deposited funds: their LP tokens become non-redeemable through the normal `Withdraw` path once the imbalance condition is reached, with no code path to recover the underlying coin/pc for that side. This matches "permanent freezing of user or LP funds," which is explicitly an accepted impact category.

### Likelihood Explanation
The precondition (one side of `total_*_without_take_pnl` becoming small relative to `amm.lp_amount`) is reachable through ordinary, permissionless protocol operation: continuous `withdrawpnl` calls by the (privileged but routine) `pnl_owner`, or normal swap activity concentrating value onto one token side over time combined with PnL extraction, particularly for token pairs with disparate decimals or low `sys_decimal_value` normalization headroom. No malicious validator or off-chain component is required — an ordinary sequence of in-scope instructions (`SwapBaseIn`/`SwapBaseOut`, `WithdrawPnl`, `Withdraw`) submitted over time can reach this state, and once reached, subsequent unprivileged `Withdraw` calls by any LP holder using attacker/user chosen `withdraw.amount` values will hit the revert deterministically.

### Recommendation
Do not use an unconditional "either computed amount is zero ⇒ revert" check as the sole gate. Instead:
- Allow zero-side settlement (transfer `0` should be skipped rather than aborting the whole instruction) when the other side is non-zero, or
- Permit a final, complete withdrawal (`withdraw.amount == amm.lp_amount`, burning the last outstanding LP units) so users are not indefinitely trapped behind the "leave at least one unit" restriction, or
- Track/report `total_*_without_take_pnl == 0` explicitly as the true cause and handle it distinctly from ordinary floor-rounding of a valid non-zero proportional share, similar to checking the true root condition rather than the derived rounded output before rejecting the withdraw.

### Proof of Concept
1. Pool is initialized normally with coin/pc reserves and `amm.lp_amount` minted to LPs.
2. `pnl_owner` repeatedly calls `WithdrawPnl` (`process_withdrawpnl`, `program/src/processor.rs:1376`) as PnL accrues from trading fees, driving `total_pc_without_take_pnl` (or `total_coin_without_take_pnl`) down relative to `amm.lp_amount`, e.g., through many swaps skewing volume to one side plus routine PnL sweeps.
3. An LP holder calls `Withdraw` (`process_withdraw`, `program/src/processor.rs:1543`) with any `withdraw.amount < amm.lp_amount` (the maximum permitted per line 1716).
4. `exchange_pool_to_token` (line 1756/1759) computes `pc_amount` (or `coin_amount`) as `total_*_without_take_pnl * withdraw.amount / amm.lp_amount`, which floors to `0` because `total_*_without_take_pnl` is small relative to `amm.lp_amount`.
5. Line 1775-1777 reverts with `AmmError::InvalidInput` for every possible `withdraw.amount` value the user can legally submit, permanently preventing that LP holder (and any other LP holder in the same situation) from redeeming their tokens through `Withdraw`.

### Citations

**File:** program/src/processor.rs (L1494-1502)
```rust
        // calc and update pnl
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```

**File:** program/src/processor.rs (L1505-1536)
```rust
        if amm.state_data.need_take_pnl_coin <= amm_coin_vault.amount
            && amm.state_data.need_take_pnl_pc <= amm_pc_vault.amount
        {
            // coin & pc is enough, transfer directly
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_coin_vault_info.clone(),
                user_pnl_coin_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                amm.state_data.need_take_pnl_coin,
            )?;
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_pc_vault_info.clone(),
                user_pnl_pc_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                amm.state_data.need_take_pnl_pc,
            )?;
            // clear need take pnl
            amm.state_data.need_take_pnl_coin = 0u64;
            amm.state_data.need_take_pnl_pc = 0u64;
            // update target_orders.calc_pnl_x & target_orders.calc_pnl_y
            target_orders.calc_pnl_x = x1.checked_sub(U128::from(delta_x)).unwrap().as_u128();
            target_orders.calc_pnl_y = y1.checked_sub(U128::from(delta_y)).unwrap().as_u128();
        } else {
            // calc error
            return Err(AmmError::TakePnlError.into());
        }
```

**File:** program/src/processor.rs (L1713-1718)
```rust
        if withdraw.amount > user_source_lp.amount {
            return Err(AmmError::InsufficientFunds.into());
        }
        if withdraw.amount > lp_mint.supply || withdraw.amount >= amm.lp_amount {
            return Err(AmmError::NotAllowZeroLP.into());
        }
```

**File:** program/src/processor.rs (L1751-1762)
```rust
        // coin_amount / total_coin_amount = amount / lp_mint.supply => coin_amount = total_coin_amount * amount / pool_mint.supply
        let invariant = InvariantPool {
            token_input: withdraw.amount,
            token_total: amm.lp_amount,
        };
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;

```

**File:** program/src/processor.rs (L1775-1777)
```rust
        if withdraw.amount == 0 || coin_amount == 0 || pc_amount == 0 {
            return Err(AmmError::InvalidInput.into());
        }
```
