### Title
Fee-on-transfer / rebasing SPL tokens allow unbacked LP minting and permanent freezing of pool accounting via `Deposit` - (File: `program/src/processor.rs`)

### Summary
Raydium's `Deposit` handler mints LP tokens and updates the pool's internal PnL invariant (`target_orders.calc_pnl_x` / `calc_pnl_y`) using the *nominal* deduced deposit amounts (`deduct_coin_amount`, `deduct_pc_amount`) rather than the amount actually credited to the AMM vault after the SPL `Transfer` executes. If the coin or pc mint of a pool is a fee-on-transfer or rebasing token, the real vault balance increase can diverge from the nominal amount used for LP-share and invariant accounting, leading to unbacked LP minting and/or a permanently reverting `CalcPnlError` in later `Deposit`/`Withdraw`/`WithdrawPnl` calls.

### Finding Description
`process_deposit` computes `deduct_coin_amount`/`deduct_pc_amount` from the user-declared `max_coin_amount`/`max_pc_amount`, computes `mint_lp_amount` from those nominal deduct amounts against the pool's *pre-transfer* vault balances, then performs the token transfer and updates the on-chain invariant using the same nominal values: [1](#0-0) [2](#0-1) 

Nowhere in this flow is the actual post-transfer vault balance (or a before/after delta) compared to `deduct_coin_amount`/`deduct_pc_amount`. `Invokers::token_transfer` blindly issues an SPL `Transfer` for the requested amount and does not verify what the destination actually received: [3](#0-2) 

For a **fee-on-transfer token**, the vault receives less than `deduct_coin_amount`/`deduct_pc_amount`, yet:
- `mint_lp_amount` was already computed using the full nominal `deduct_coin_amount` as numerator (`InvariantPool::exchange_token_to_pool`), so the depositor is credited LP shares as if the full amount arrived — diluting existing LPs (unbacked LP minting).
- `target_orders.calc_pnl_x`/`calc_pnl_y` are advanced by the nominal normalized amount, permanently overstating the invariant relative to the real (lower) vault balance.

For a **rebasing token**, the vault balance itself changes outside of any transfer, but the separately-tracked invariant (`calc_pnl_x`/`calc_pnl_y`, and `amm.state_data.need_take_pnl_pc/coin`) is only updated on deposit/withdraw/swap events using computed nominal deltas, so it can drift from the live balance used elsewhere.

This drift is dangerous because `calc_take_pnl` — invoked by `Deposit`, `Withdraw`, and `WithdrawPnl` — asserts that the real pool `k` (live vault balances) is greater than or equal to the tracked invariant `k` (derived from `calc_pnl_x`/`calc_pnl_y`), and hard-errors otherwise: [4](#0-3) [5](#0-4) 

Once the tracked invariant permanently exceeds the real balance (a natural consequence of fee-on-transfer deductions or negative rebases lowering real balances below what was recorded), every subsequent `Deposit`, `Withdraw`, and `WithdrawPnl` call reverts with `AmmError::CalcPnlError`, freezing depositors' and LPs' ability to add/remove liquidity or take PnL, while swap-only paths (`SwapBaseIn`/`SwapBaseOut`, which read live vault balances via `calc_total_without_take_pnl_no_orderbook` and don't call `calc_take_pnl`) may still drain the mispriced pool: [6](#0-5) 

The pool mint/coin/pc mints are attacker-controlled at `Initialize2` time (any user can create a pool for an arbitrary market/mint pair), so an unprivileged pool creator can set up a pool backed by a fee-on-transfer or rebasing token and then deposit to trigger this.

### Impact Explanation
This can result in: (1) unbacked LP token minting when the token has transfer fees, directly diluting/stealing value from other liquidity providers; and (2) permanent freezing of `Deposit`/`Withdraw`/`WithdrawPnl` functionality for a pool once the internally tracked PnL invariant exceeds real balances, locking user and protocol funds. Both are concrete fund-loss/freezing impacts, matching High severity.

### Likelihood Explanation
Any unprivileged user can call `Initialize2` to create a pool with an arbitrary coin/pc mint (including a fee-on-transfer or rebasing token) and then call `Deposit` with attacker-chosen amounts — no privileged signer or special build is required. Fee-on-transfer and rebasing tokens are common on Solana-adjacent/token-2022-style ecosystems, making this a realistic misuse path rather than a purely theoretical one.

### Recommendation
Measure the actual token amount received by the vault (read vault balance immediately before and after the `token_transfer` CPI) and use that real delta — not the nominal `deduct_coin_amount`/`deduct_pc_amount`/`swap.amount_in` — for LP-mint calculations and for updating `target_orders.calc_pnl_x`/`calc_pnl_y`/`need_take_pnl_*`. Alternatively, explicitly disallow initialization of pools whose coin/pc mint has non-standard transfer semantics (fee-on-transfer, rebasing, transfer hooks).

### Proof of Concept
1. Attacker creates an SPL mint `M` with a transfer fee (or a rebasing supply mechanism) and calls `Initialize2` to create an AMM pool with `coin_mint = M`.
2. Attacker calls `Deposit` with `max_coin_amount = X`. `deduct_coin_amount` is computed as `X` (or a ratio thereof); `mint_lp_amount` is computed from `X` against the pool's pre-transfer coin total (`program/src/processor.rs:1244-1250`).
3. `Invokers::token_transfer(..., X)` is issued, but due to the fee-on-transfer mechanism the vault actually receives `X' < X` (`program/src/invokers.rs:148-168`).
4. `target_orders.calc_pnl_y` is incremented by `normalize_decimal_v2(X, ...)` (the nominal amount), not `X'` (`program/src/processor.rs:1362-1371`), while `amm.lp_amount` is increased by the full `mint_lp_amount` computed from `X`.
5. Over repeated deposits, the tracked invariant (`calc_pnl_x * calc_pnl_y`) grows faster than the real vault product, until `calc_take_pnl`'s assertion at `program/src/processor.rs:190-192` fails, returning `AmmError::CalcPnlError` (line 277) on every future `Deposit`/`Withdraw`/`WithdrawPnl` call — permanently freezing those operations for the pool, while LP shares minted in step 2-4 remain overvalued relative to actual backing.

### Citations

**File:** program/src/processor.rs (L188-192)
```rust
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L267-278)
```rust
        } else {
            msg!(arrform!(
                LOG_SIZE,
                "calc_take_pnl error x:{}, y:{}, calc_pnl_x:{}, calc_pnl_y:{}",
                x1,
                y1,
                identity(target.calc_pnl_x),
                identity(target.calc_pnl_y)
            )
            .as_str());
            return Err(AmmError::CalcPnlError.into());
        }
```

**File:** program/src/processor.rs (L1243-1250)
```rust
            // coin_amount/ (total_coin_amount + coin_amount)  = output / (lp_mint.supply + output) =>  output = coin_amount / total_coin_amount * lp_mint.supply
            let invariant_coin = InvariantPool {
                token_input: deduct_coin_amount,
                token_total: total_coin_without_take_pnl,
            };
            mint_lp_amount = invariant_coin
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1327-1372)
```rust
        Invokers::token_transfer(
            token_program_info.clone(),
            user_source_coin_info.clone(),
            amm_coin_vault_info.clone(),
            source_owner_info.clone(),
            deduct_coin_amount,
        )?;
        Invokers::token_transfer(
            token_program_info.clone(),
            user_source_pc_info.clone(),
            amm_pc_vault_info.clone(),
            source_owner_info.clone(),
            deduct_pc_amount,
        )?;
        Invokers::token_mint_to(
            token_program_info.clone(),
            amm_lp_mint_info.clone(),
            user_dest_lp_info.clone(),
            amm_authority_info.clone(),
            AUTHORITY_AMM,
            amm.nonce as u8,
            mint_lp_amount,
        )?;
        amm.lp_amount = amm.lp_amount.checked_add(mint_lp_amount).unwrap();

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
        amm.recent_epoch = Clock::get()?.epoch;
```

**File:** program/src/invokers.rs (L148-168)
```rust
    pub fn token_transfer<'a>(
        token_program: AccountInfo<'a>,
        source: AccountInfo<'a>,
        destination: AccountInfo<'a>,
        owner: AccountInfo<'a>,
        deposit_amount: u64,
    ) -> Result<(), ProgramError> {
        let ix = spl_token::instruction::transfer(
            token_program.key,
            source.key,
            destination.key,
            owner.key,
            &[],
            deposit_amount,
        )?;
        solana_program::program::invoke_signed(
            &ix,
            &[source, destination, owner, token_program],
            &[],
        )
    }
```

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
