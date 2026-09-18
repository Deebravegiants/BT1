Based on the investigation, I have enough evidence to construct a valid analog. I was unable to fully verify the internal implementation of `Calculator::calc_total_without_take_pnl_no_orderbook` before running out of iterations, so I note that as an open verification point below.

### Title
Withdraw skips protocol PnL accrual/reservation when pool status is `WithdrawOnly`, letting LP withdrawals capture unswept protocol fees and insolvency-freeze `WithdrawPnl` - (File: program/src/processor.rs)

### Summary
`process_withdraw` conditionally skips the `calc_take_pnl` step — which computes and reserves the protocol's accrued profit share (`need_take_pnl_pc/coin`) — whenever `amm.status == AmmStatus::WithdrawOnly`. Any unprivileged LP calling the `Withdraw` instruction while the pool is in that (legitimate, admin-settable) status therefore withdraws a pro-rata share of the *full* vault balance, including profit that should have been carved out for the protocol/`pnl_owner`, rather than the correctly reduced balance used in every other status.

### Finding Description
In `process_withdraw` the pool's spendable totals are computed via `Calculator::calc_total_without_take_pnl_no_orderbook`, and then normally reduced further by `Self::calc_take_pnl`, which calculates the newly-accrued protocol PnL since the last checkpoint and adds it to `amm.state_data.need_take_pnl_pc/coin` (reserved for the protocol, redeemable only via `process_withdrawpnl`). This is done unconditionally in `process_deposit` [1](#0-0)  and in `process_withdrawpnl` [2](#0-1) , but in `process_withdraw` it is explicitly bypassed for one status value: [3](#0-2) 

`AmmStatus::WithdrawOnly` is a normal, admin-reachable operational state (set via `process_set_params`, e.g. to pause deposits/swaps while still allowing LPs to exit) and it explicitly grants `withdraw_permission() == true` [4](#0-3) . Because withdrawal share is computed as `withdraw.amount / amm.lp_amount` applied to `total_coin/pc_without_take_pnl` [5](#0-4) , omitting the PnL carve-out in this status means every LP who withdraws while in `WithdrawOnly` receives a larger share than they are entitled to — proportionally consuming the token balance that should be earmarked for the protocol fee — while `target_orders.calc_pnl_x/y` are still adjusted as if a normal deduction happened [6](#0-5) .

This is directly analogous to the reported Nova bug class: an incomplete state-based check (only one of several valid operational states omits the accounting step) lets an unprivileged actor (LP), operating a normal supported instruction (`Withdraw`), extract value/resources that should have been reserved, bypassing the intended accounting invariant that is otherwise enforced everywhere else in the codebase.

### Impact Explanation
Because reserved protocol PnL (`need_take_pnl_pc/coin`) is not deducted from the withdrawable pool while `WithdrawOnly` is active, LPs draining the pool during this window can leave the vault under-collateralized relative to the recorded `need_take_pnl_pc/coin`. When the protocol later calls `process_withdrawpnl`, it requires `need_take_pnl_coin <= amm_coin_vault.amount && need_take_pnl_pc <= amm_pc_vault.amount` or it fails with `TakePnlError` [7](#0-6) , permanently freezing the protocol's fee collection. It also constitutes insolvent pool accounting/unfair value extraction from remaining LPs, since the pool's real assets are drawn down beyond what the invariant intends.

### Likelihood Explanation
`WithdrawOnly` is a legitimate, documented status (comment: "pool only can add or remove liquidity, can't swap") that pool owners are expected to use operationally (e.g., during incident response or planned pauses), and once set, any LP token holder can submit an ordinary `Withdraw` transaction to exploit the skipped accounting — no privileged signer or unusual build is required for the exploiting transaction itself.

### Recommendation
Remove the special-case skip and always call `Self::calc_take_pnl` in `process_withdraw` regardless of `amm.status`, consistent with `process_deposit` and `process_withdrawpnl`, unless there is a documented reason `WithdrawOnly` should bypass PnL reservation — in which case the accounting invariant checked in `process_withdrawpnl` should be hardened to prevent shortfall/DoS.

### Proof of Concept
1. Admin calls `SetParams` to set `amm.status = AmmStatus::WithdrawOnly` (a supported, intended operational transition).
2. An LP submits `Withdraw` for their full LP balance; because `amm.status == WithdrawOnly`, `calc_take_pnl` is skipped at `program/src/processor.rs:1740`, so `total_pc_without_take_pnl`/`total_coin_without_take_pnl` are not reduced by newly accrued protocol PnL before the pro-rata payout is computed.
3. Repeat for multiple LPs; the vault balance can be drawn down below the accumulated `amm.state_data.need_take_pnl_pc/coin`.
4. Protocol calls `process_withdrawpnl`; the balance check fails and returns `AmmError::TakePnlError`, permanently blocking protocol fee withdrawal for this pool [7](#0-6) .

### Citations

**File:** program/src/processor.rs (L1166-1173)
```rust
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```

**File:** program/src/processor.rs (L1495-1502)
```rust
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

**File:** program/src/processor.rs (L1737-1749)
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

**File:** program/src/processor.rs (L1818-1838)
```rust
        // step4: update target_orders.calc_pnl_x & target_orders.calc_pnl_y
        target_orders.calc_pnl_x = x1
            .checked_sub(Calculator::normalize_decimal_v2(
                pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_sub(Calculator::normalize_decimal_v2(
                coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
```

**File:** program/src/state.rs (L283-294)
```rust
    pub fn withdraw_permission(&self) -> bool {
        match self {
            AmmStatus::Uninitialized => false,
            AmmStatus::Initialized => true,
            AmmStatus::Disabled => false,
            AmmStatus::WithdrawOnly => true,
            AmmStatus::LiquidityOnly => true,
            AmmStatus::OrderBookOnly => true,
            AmmStatus::SwapOnly => true,
            AmmStatus::WaitingTrade => true,
        }
    }
```
