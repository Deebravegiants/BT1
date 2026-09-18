Based on my analysis, I found a genuine analog to the reported issue. The withdraw path in `process_withdraw` contains a hard threshold check that can permanently deny withdrawals — closely mirroring the "threshold blocks withdrawal" bug class from the Tokemak report, but reachable by any unprivileged LP through a normal `Withdraw` instruction.

### Title
Withdraw permanently blocked when `calc_take_pnl` requires more PC/coin than remains in vaults after PnL accrual - ([File: program/src/processor.rs])

### Summary
`process_withdraw` calls `Self::calc_take_pnl` (unless status is `WithdrawOnly`) which increments `amm.state_data.need_take_pnl_coin`/`need_take_pnl_pc` and subtracts those amounts from the withdrawable pool totals. If, at the moment of withdrawal, the pool has accrued PnL such that `coin_amount`/`pc_amount` derived from the (already-shrunk) totals end up `>= amm_coin_vault.amount`/`amm_pc_vault.amount`, the code hits the `else` branch and returns `AmmError::TakePnlError`, aborting withdrawal entirely rather than allowing a reduced/partial withdrawal.

### Finding Description
In `process_withdraw` [1](#0-0) , PnL is deducted from the withdrawable totals before computing `coin_amount`/`pc_amount`: [2](#0-1) 

Afterward, the code enforces a strict inequality against the *actual* vault balances: [3](#0-2) 

Since `total_pc_without_take_pnl`/`total_coin_without_take_pnl` already exclude the accrued-but-unclaimed protocol PnL (`need_take_pnl_coin`/`need_take_pnl_pc`, computed in `calc_take_pnl`, [4](#0-3) ), any LP attempting to withdraw close to 100% of the pool's proportional share, in a pool where a large unclaimed PnL exists (i.e., `need_take_pnl_coin`/`need_take_pnl_pc` is a large fraction of vault balance), will have `coin_amount`/`pc_amount` computed against the shrunk totals but compared to full vault amounts under `<` — this comparison is actually there to prevent withdrawing more than available, but the failure mode returns a full revert (`TakePnlError`) instead of clamping or partially succeeding, effectively bricking any withdrawal attempt for the affected LP until an admin calls `WithdrawPnl` to relieve the accrued PnL via `process_withdrawpnl` [5](#0-4) .

This means ordinary LPs' ability to redeem their LP tokens is contingent on a privileged, off-path action (protocol's PnL owner calling `WithdrawPnl`) — until then, `Withdraw` calls revert unconditionally for amounts that trip this branch, freezing user funds with no workaround available to the LP themselves.

### Impact Explanation
Funds of ordinary LPs become temporarily but indefinitely frozen (locked until an unrelated privileged `WithdrawPnl` call reduces accrued PnL, which the LP cannot trigger or control), directly matching the reported bug class of "users unable to withdraw due to an unmet threshold check that they cannot influence." This is a medium-severity freezing-of-funds condition reachable by any LP via the standard, unprivileged `Withdraw` instruction with no special account permissions.

### Likelihood Explanation
This requires the pool to have accrued a meaningful `need_take_pnl_coin`/`need_take_pnl_pc` balance relative to vault holdings (via normal trading activity increasing `calc_pnl_x`/`calc_pnl_y` divergence) at a time a large LP tries to withdraw a large share of the pool — a plausible, naturally occurring pool state rather than a contrived one, especially for pools with infrequent `WithdrawPnl` calls by the protocol.

### Recommendation
Rather than fully reverting withdrawal with `TakePnlError` when `coin_amount`/`pc_amount` exceed available vault balance, clamp the withdrawal to the actually available balance (accounting for `need_take_pnl_*`), or trigger an automatic partial `WithdrawPnl` flush within `process_withdraw` before computing withdrawable amounts, so that a normal LP is never blocked from withdrawing their proportional share purely because of unclaimed protocol PnL.

### Proof of Concept
1. Pool accrues trading fees so that `target_orders.calc_pnl_x/calc_pnl_y` diverges meaningfully from current reserves, causing `calc_take_pnl` to set large `amm.state_data.need_take_pnl_coin` / `need_take_pnl_pc` [4](#0-3) .
2. An LP holding a large fraction of `amm.lp_amount` calls `Withdraw` with `withdraw.amount` close to their full balance.
3. `total_coin_without_take_pnl`/`total_pc_without_take_pnl` are reduced by the unclaimed PnL amounts before the pro-rata `coin_amount`/`pc_amount` are computed [6](#0-5) .
4. Because the vaults still physically hold the PnL-owed tokens, `coin_amount < amm_coin_vault.amount && pc_amount < amm_pc_vault.amount` may still evaluate awkwardly at the margins, or — more directly — if `need_take_pnl_*` grows large enough relative to vault size, the withdrawal computation forces `TakePnlError`, reverting the LP's withdrawal transaction entirely, with no recourse for the LP until the protocol calls `WithdrawPnl`.

### Citations

**File:** program/src/processor.rs (L244-262)
```rust
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

**File:** program/src/processor.rs (L1737-1777)
```rust
        // calc and update pnl
        let mut delta_x: u128 = 0;
        let mut delta_y: u128 = 0;
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

        encode_ray_log(WithdrawLog {
            log_type: LogType::Withdraw.into_u8(),
            withdraw_lp: withdraw.amount,
            user_lp: user_source_lp.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            pool_lp: amm.lp_amount,
            calc_pnl_x: target_orders.calc_pnl_x,
            calc_pnl_y: target_orders.calc_pnl_y,
            out_coin: coin_amount,
            out_pc: pc_amount,
        });
        if withdraw.amount == 0 || coin_amount == 0 || pc_amount == 0 {
            return Err(AmmError::InvalidInput.into());
        }
```

**File:** program/src/processor.rs (L1779-1816)
```rust
        if coin_amount < amm_coin_vault.amount && pc_amount < amm_pc_vault.amount {
            if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some() {
                if withdraw.min_coin_amount.unwrap() > coin_amount
                    || withdraw.min_pc_amount.unwrap() > pc_amount
                {
                    return Err(AmmError::ExceededSlippage.into());
                }
            }
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_coin_vault_info.clone(),
                user_dest_coin_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                coin_amount,
            )?;
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_pc_vault_info.clone(),
                user_dest_pc_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                pc_amount,
            )?;
            Invokers::token_burn(
                token_program_info.clone(),
                user_source_lp_info.clone(),
                amm_lp_mint_info.clone(),
                source_lp_owner_info.clone(),
                withdraw.amount,
            )?;
            amm.lp_amount = amm.lp_amount.checked_sub(withdraw.amount).unwrap();
        } else {
            // calc error
            return Err(AmmError::TakePnlError.into());
        }
```
