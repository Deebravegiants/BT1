### Title
Underflow in `calc_total_without_take_pnl_no_orderbook` can permanently freeze a pool's swaps, deposits and withdrawals - (File: `program/src/math.rs`)

### Summary
Every state-changing pool instruction (`SwapBaseIn`, `SwapBaseOut`, `Deposit`, `Withdraw`, `WithdrawPnl`) first calls `Calculator::calc_total_without_take_pnl_no_orderbook` to compute the pool's "logical" reserves net of the protocol's accrued-but-unwithdrawn PnL (`need_take_pnl_pc` / `need_take_pnl_coin`). This mirrors the reported bug class: an accounting value that is subtracted from a balance can, under certain conditions, exceed that balance and cause a revert that blocks all subsequent user operations, freezing funds in the pool.

### Finding Description
`calc_total_without_take_pnl_no_orderbook` subtracts the amm's accrued but unwithdrawn protocol PnL from the raw vault balances: [1](#0-0) 

This function is invoked, using a checked subtraction that returns `AmmError::CheckedSubOverflow` on underflow, at the start of `process_swap_base_in`: [2](#0-1) 

as well as in `process_deposit`, `process_withdraw`, and `process_withdrawpnl` itself: [3](#0-2) [4](#0-3) 

`need_take_pnl_pc`/`need_take_pnl_coin` are accumulated by `calc_take_pnl` on every `Deposit`/`Withdraw`/`WithdrawPnl` call, growing over time as more PnL is recognized from the pool's growth relative to `target.calc_pnl_x`/`target.calc_pnl_y`: [5](#0-4) 

`process_withdrawpnl` even anticipates that these accrued values may exceed the *actual raw* vault balances at the time PnL is finally withdrawn, guarding the token transfers with an explicit check that returns `AmmError::TakePnlError` if `need_take_pnl_coin > amm_coin_vault.amount` or `need_take_pnl_pc > amm_pc_vault.amount`: [6](#0-5) 

However, that safety check happens *after* `calc_total_without_take_pnl_no_orderbook` has already been called earlier in the same function (line 1459-1464) using the *stored* `need_take_pnl_pc`/`need_take_pnl_coin` values from `amm.state_data`. If those stored values are already larger than the current raw vault balances (e.g., due to rounding drift accumulated across many `Deposit`/`Withdraw`/`WithdrawPnl` cycles through `Calculator::restore_decimal`/`normalize_decimal_v2`, or via any sequence that leaves the vault balance lower than the recognized-but-unclaimed PnL), the very first call to `calc_total_without_take_pnl_no_orderbook` underflows and reverts with `CheckedSubOverflow` — before the `TakePnlError` guard is ever reached.

### Impact Explanation
Because `calc_total_without_take_pnl_no_orderbook` is called unconditionally at the top of `process_swap_base_in`, `process_swap_base_out`, `process_deposit`, `process_withdraw`, and `process_withdrawpnl`, once `need_take_pnl_pc`/`need_take_pnl_coin` exceeds the actual vault balance, **every** instruction on that pool reverts — including `WithdrawPnl`, which was the intended recovery path. This is a stronger variant of the reported issue: in the original report, only the cancel-quote path was blocked and could be unblocked once the fee collector redeposited funds; here, the recovery instruction (`WithdrawPnl`) itself is unreachable because it fails on the same underflow before its own `TakePnlError` safety check executes. This would permanently freeze all LP and swap funds in the affected pool.

### Likelihood Explanation
This requires the accumulated `need_take_pnl_pc`/`need_take_pnl_coin` state to drift above the true vault balance. The codebase's own defensive check in `process_withdrawpnl` (`TakePnlError`) shows the developers anticipated this state is reachable, but I could not conclusively trace, from static code reading alone, the exact sequence of decimal-normalization roundings (`restore_decimal`/`normalize_decimal_v2` in `calc_take_pnl`, `process_deposit`, `process_withdraw`) that would push `need_take_pnl_*` strictly above the raw vault balance in practice. This would need to be confirmed with a concrete numeric/fuzz test of `calc_take_pnl` across many deposit/withdraw cycles with adversarial decimal choices, which is out of scope for static analysis.

### Recommendation
Have `calc_total_without_take_pnl_no_orderbook` (and all call sites) use `saturating_sub` or an explicit bounds clamp instead of a hard `checked_sub` that reverts the whole instruction, and ensure `process_withdrawpnl` can always execute (even partially) to reconcile `need_take_pnl_pc`/`need_take_pnl_coin` down to the real vault balance rather than reverting outright — so a stuck pool can always be repaired via `WithdrawPnl` regardless of how large the drift has become.

### Proof of Concept
Not independently reproduced with a runnable test; based on static tracing of `calc_take_pnl` → `state_data.need_take_pnl_pc/coin` accumulation and its unconditional consumption via `checked_sub` in `calc_total_without_take_pnl_no_orderbook` at the entry of `process_swap_base_in`/`process_swap_base_out`/`process_deposit`/`process_withdraw`/`process_withdrawpnl`. A concrete PoC would require driving repeated `Deposit`/`Withdraw`/`WithdrawPnl` sequences with rounding-adversarial amounts to push `need_take_pnl_pc` or `need_take_pnl_coin` above the corresponding vault's raw token balance, then observing that any subsequent instruction (including `WithdrawPnl`) reverts with `CheckedSubOverflow`.

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

**File:** program/src/processor.rs (L1147-1153)
```rust
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1458-1464)
```rust
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
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

**File:** program/src/processor.rs (L1940-1945)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```
