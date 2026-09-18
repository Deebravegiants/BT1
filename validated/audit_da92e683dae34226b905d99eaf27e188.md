## Title
Manipulable instantaneous pool price used to compute LP "PnL" skim in `calc_take_pnl` during permissionless `Deposit`/`Withdraw` - (File: `program/src/processor.rs`)

## Summary
`Processor::calc_take_pnl` determines how much of the pool's reserves are diverted from LP-backing liquidity into the privileged `need_take_pnl_pc` / `need_take_pnl_coin` bucket (later swept by the trusted `pnl_owner` via `process_withdrawpnl`). This calculation is driven entirely by the *live* AMM vault balances read at the moment `Deposit` or `Withdraw` executes, with no TWAP or oracle protection. Because `Deposit`/`Withdraw` are permissionless and any user can compose arbitrary instructions (including swaps) in the same atomic transaction, an attacker can momentarily skew the coin/pc reserve ratio, trigger the PnL skim against that skewed ratio, then restore the price — analogous to the reported USSD `rebalance()` flashloan price-manipulation issue, where a price read from a manipulable AMM pool drives a critical protocol-state update within a single transaction.

## Finding Description
`calc_take_pnl` is invoked from `process_deposit` [1](#0-0)  and `process_withdraw` [2](#0-1) , using `x1`/`y1` that are normalized directly from the current `amm_pc_vault.amount` / `amm_coin_vault.amount` (i.e., the pool's instantaneous, swap-manipulable reserves) [3](#0-2) .

Inside `calc_take_pnl`, the function computes a "fair" point `(x2, y2)` on the last recorded constant-product curve (`target.calc_pnl_x * target.calc_pnl_y`) that matches the *current* instantaneous price ratio `x1/y1`, via `calc_x_power` (`x2_power = last_x*last_y*current_x/current_y`) [4](#0-3) . The difference `diff_x = x1 - x2`, `diff_y = y1 - y2` is then partially skimmed (`pnl_numerator/pnl_denominator`) out of `total_pc_without_take_pnl`/`total_coin_without_take_pnl` and permanently booked into `amm.state_data.need_take_pnl_pc/coin` for the privileged `pnl_owner` [5](#0-4) .

Because `x1/y1` is simply the pool's current spot price, an attacker can, within one transaction:
1. Execute a large swap (`SwapBaseIn`/`SwapBaseOut`) to sharply move the coin/pc reserve ratio.
2. Immediately call `Deposit` or `Withdraw`, causing `calc_take_pnl` to compute `x2/y2` against this manipulated price, producing a `diff_x`/`diff_y` that does not correspond to genuine accumulated trading-fee growth of the pool but to an artificially skewed price snapshot.
3. Reverse the swap to restore price.

The resulting `need_take_pnl_pc`/`need_take_pnl_coin` increase permanently reduces `total_pc_without_take_pnl`/`total_coin_without_take_pnl`, i.e., the actual reserves backing LP withdrawals [6](#0-5) , and `target_orders.calc_pnl_x/y` are updated to the manipulated checkpoint [7](#0-6) . This value is not retrievable by LPs; it is only claimable by the trusted `pnl_owner` in `process_withdrawpnl` [8](#0-7) . No swap instruction itself invokes `calc_take_pnl`, so the skim only fires at `Deposit`/`Withdraw` checkpoints — exactly the state-changing entry points an attacker can pair with a same-transaction price manipulation, mirroring the reported bug class of "read manipulable pool price then immediately act on it."

## Impact Explanation
This causes insolvent pool accounting: value that should remain to back LP share redemptions is diverted into the pnl-owner-claimable bucket based on an artificially manipulated instantaneous price rather than genuine, organically accrued trading fees. Every future depositor/withdrawer redeems against a reserve pool that has been under-stated relative to `lp_amount`, permanently disadvantaging LPs in favor of a privileged party triggered entirely by an unprivileged, single-transaction actor.

## Likelihood Explanation
`Deposit`, `Withdraw`, and the four swap instructions are all unprivileged, and Solana transactions can freely compose a swap followed by a `Deposit`/`Withdraw` in one atomic transaction with attacker-chosen amounts, so the precondition (spot-price manipulation immediately before the PnL checkpoint) is trivially reachable by any user, particularly on lower-liquidity pools where price impact per swap is large.

## Recommendation
Do not derive the PnL skim from the instantaneous vault balances at `Deposit`/`Withdraw` time. Use a time-weighted or otherwise manipulation-resistant price/reserve measure (e.g., accrue PnL incrementally on every swap based on realized fee amounts rather than an end-of-window price snapshot), or bound the allowed price deviation between consecutive `calc_take_pnl` calls before permitting the skim to execute.

## Proof of Concept
1. Attacker submits a single transaction containing:
   - Instruction 1: `SwapBaseIn`/`SwapBaseOut` with a large `amount_in` skewing `amm_coin_vault`/`amm_pc_vault` ratio far from the ratio implied by `target_orders.calc_pnl_x/calc_pnl_y`.
   - Instruction 2: `Deposit` (or `Withdraw`) on the same AMM, which reads the now-skewed vault balances into `total_pc_without_take_pnl`/`total_coin_without_take_pnl` and calls `calc_take_pnl` [9](#0-8) , causing an inflated `diff_x`/`diff_y` to be computed against the manipulated `x1/y1` and booked into `need_take_pnl_pc/coin` [5](#0-4) .
   - Instruction 3: an opposite-direction swap restoring the pool price to its original level.
2. After the transaction, `amm.state_data.need_take_pnl_pc/coin` reflect an inflated skim not backed by genuine trading-fee growth, and `total_pc_without_take_pnl`/`total_coin_without_take_pnl` used for subsequent LP withdrawals are correspondingly reduced, degrading the funds available to LPs relative to their `lp_amount` share.

### Citations

**File:** program/src/processor.rs (L211-262)
```rust
            // transfer to token_coin_pnl and token_pc_pnl
            // (x1 -x2) * pnl / sys_decimal_value
            let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
            let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
            delta_x = diff_x
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();
            delta_y = diff_y
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();

            let diff_pc_pnl_amount =
                Calculator::restore_decimal(diff_x, amm.pc_decimals, amm.sys_decimal_value);
            let diff_coin_pnl_amount =
                Calculator::restore_decimal(diff_y, amm.coin_decimals, amm.sys_decimal_value);
            let pc_pnl_amount = diff_pc_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
            let coin_pnl_amount = diff_coin_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
            if pc_pnl_amount != 0 && coin_pnl_amount != 0 {
                amm.state_data.need_take_pnl_pc = amm
                    .state_data
                    .need_take_pnl_pc
                    .checked_add(pc_pnl_amount)
                    .unwrap();
                amm.state_data.need_take_pnl_coin = amm
                    .state_data
                    .need_take_pnl_coin
                    .checked_add(coin_pnl_amount)
                    .unwrap();

                // step3: update total_coin and total_pc without pnl
                *total_pc_without_take_pnl = (*total_pc_without_take_pnl)
                    .checked_sub(pc_pnl_amount)
                    .unwrap();
                *total_coin_without_take_pnl = (*total_coin_without_take_pnl)
                    .checked_sub(coin_pnl_amount)
                    .unwrap();
```

**File:** program/src/processor.rs (L1148-1173)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
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

**File:** program/src/processor.rs (L1352-1371)
```rust
        target_orders.calc_pnl_x = x1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
```

**File:** program/src/processor.rs (L1505-1526)
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
```

**File:** program/src/processor.rs (L1740-1749)
```rust
        if amm.status != AmmStatus::WithdrawOnly.into_u64() {
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
        }
```

**File:** program/src/processor.rs (L1751-1761)
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

**File:** program/src/math.rs (L50-60)
```rust
    pub fn calc_x_power(last_x: U256, last_y: U256, current_x: U256, current_y: U256) -> U256 {
        // must be use u256, because u128 may be overflow
        let x_power = last_x
            .checked_mul(last_y)
            .unwrap()
            .checked_mul(current_x)
            .unwrap()
            .checked_div(current_y)
            .unwrap();
        x_power
    }
```
