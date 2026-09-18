### Title
Unhandled arithmetic panics in `calc_take_pnl` can permanently freeze a pool - (File: `program/src/processor.rs`)

### Summary
The Lombard report's bug class is "an unhandled panic on attacker-influenced input causes the service to stop working, disrupting the protocol." The direct analog in `raydium-amm` is `Processor::calc_take_pnl`, which is invoked from every reachable state-changing instruction (`process_deposit`, `process_withdraw`, `process_swap_base_in`, `process_swap_base_out`, `process_swap_base_in_v2`, `process_swap_base_out_v2`, `process_withdrawpnl`) and performs a chain of `.unwrap()` arithmetic operations instead of returning a `ProgramError`. [1](#0-0) 

### Finding Description
Inside `calc_take_pnl`, once the branch condition `pool_pc_amount.checked_mul(pool_coin_amount).unwrap() >= calc_pc_amount.checked_mul(calc_coin_amount).unwrap()` is taken, every subsequent arithmetic step is performed with bare `.unwrap()` rather than propagating an error: [2](#0-1) 

Notably, `diff_x`/`diff_y` are computed with `checked_sub(...).unwrap()` on the results of an integer square-root approximation (`x2_power.integer_sqrt()`), which can legitimately return a value larger than `x1`/`y1` due to rounding, causing an underflow panic: [3](#0-2) 

The subsequent additions to `state_data.need_take_pnl_pc/coin` and subtractions from `total_pc_without_take_pnl`/`total_coin_without_take_pnl` are also unwrap-based: [4](#0-3) 

Contrast this with the `else` branch of the same function, which handles the analogous "invalid state" condition gracefully by returning `Err(AmmError::CalcPnlError)` instead of panicking: [5](#0-4) 

`total_pc_without_take_pnl`/`total_coin_without_take_pnl` are derived from live vault token balances (`amm_pc_vault.amount`, `amm_coin_vault.amount`), while `target.calc_pnl_x`/`target.calc_pnl_y` are persisted state only updated inside this same function. Because the AMM's coin/pc vaults are ordinary SPL Token accounts owned by the program's PDA authority, **any unprivileged actor can transfer (donate) additional tokens directly into `amm_coin_vault`/`amm_pc_vault` without going through `Deposit` or `Swap`**, skewing the ratio between the live vault balances and the persisted `calc_pnl_x`/`calc_pnl_y` baseline. This is a well-known "donation" vector for constant-product AMMs and is directly reachable by a single transaction with attacker-chosen accounts/data (an SPL `Transfer` to the vault ATA), which satisfies the "single submitted transaction with attacker-chosen accounts and data" bar.

### Impact Explanation
Because `calc_take_pnl` is called by every fund-moving instruction (`Deposit`, `Withdraw`, `SwapBaseIn(V2)`, `SwapBaseOut(V2)`, `WithdrawPnl`), if a donation pushes the ratio into a region where the integer-sqrt rounding causes `x2 > x1` or `y2 > y1`, the `checked_sub().unwrap()` at lines 213–214 will panic on every future call to any of these instructions for that pool. Since the panic is deterministic given the (now permanently skewed) persisted state and there is no instruction path that can correct `target.calc_pnl_x`/`calc_pnl_y` without itself calling `calc_take_pnl`, the pool becomes permanently unusable — LPs cannot withdraw and swappers cannot trade, i.e., permanent freezing of user/LP funds, unlike the original off-chain report where the panic only crashed a single node process that could be restarted.

### Likelihood Explanation
Triggering the underlying underflow requires finding vault-balance/`calc_pnl` ratios where the integer-sqrt rounding produces `x2 > x1` (or `y2 > y1`) — I was not able to fully verify the exact numeric conditions of `Calculator::calc_x_power`/`integer_sqrt` within the available indexed contents of `program/src/math.rs`, so I cannot confirm the precise donation amount/ratio needed to trigger the panic deterministically. The attack primitive itself (unprivileged SPL token transfer directly to the AMM vault) is trivially reachable and requires no special privilege, but confirming exact exploitability requires deeper numeric analysis of `math.rs` that the current index did not fully surface.

### Recommendation
Replace the `.unwrap()` calls in the "if" branch of `calc_take_pnl` (particularly the `checked_sub` calls computing `diff_x`/`diff_y`, and all downstream `checked_mul`/`checked_div`/`checked_add` calls) with proper `ok_or(AmmError::CalcPnlError)?`-style error propagation, mirroring the existing `else` branch. This ensures that any unexpected state (including one induced by external vault donations) results in a clean instruction failure rather than a panic, and ideally also add saturating/clamping logic so donation-induced skew cannot permanently deadlock the pool's core instructions.

### Proof of Concept
1. Attacker identifies a target AMM pool and its `amm_coin_vault`/`amm_pc_vault` SPL token accounts (public, derived via PDA, addresses are public in `AmmInfo`).
2. Attacker submits a standard SPL Token `Transfer` instruction sending a large amount of the coin or pc token directly into the vault account (no AMM instruction involved, no signer/privilege required beyond owning the tokens).
3. On the next `Deposit`, `Withdraw`, `SwapBaseIn(V2)`, `SwapBaseOut(V2)`, or `WithdrawPnl` call, `calc_take_pnl` recomputes `total_pc_without_take_pnl`/`total_coin_without_take_pnl` from the now-inflated vault balances against the stale `target.calc_pnl_x/y`, and (depending on the exact ratio, unverified precisely due to missing `math.rs` content) causes a checked-subtraction/unwrap panic.
4. All subsequent calls into any of the above instructions repeat the same computation against the same skewed persisted state and panic identically, permanently locking user and LP funds in the pool. [6](#0-5) [7](#0-6)

### Citations

**File:** program/src/processor.rs (L167-174)
```rust
    pub fn calc_take_pnl(
        target: &TargetOrders,
        amm: &mut AmmInfo,
        total_pc_without_take_pnl: &mut u64,
        total_coin_without_take_pnl: &mut u64,
        x1: U256,
        y1: U256,
    ) -> Result<(u128, u128), ProgramError> {
```

**File:** program/src/processor.rs (L190-226)
```rust
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
            // last k is
            // let last_k: u128 = (target.calc_pnl_x as u128).checked_mul(target.calc_pnl_y as u128).unwrap();
            // current k is
            // let current_k: u128 = (x1 as u128).checked_mul(y1 as u128).unwrap();
            // current p is
            // let current_p: u128 = (x1 as u128).checked_div(y1 as u128).unwrap();
            let x2_power = Calculator::calc_x_power(
                target.calc_pnl_x.into(),
                target.calc_pnl_y.into(),
                x1,
                y1,
            );
            // let x2 = Calculator::sqrt(x2_power).unwrap();
            let x2 = x2_power.integer_sqrt();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl x2_power:{}, x2:{}", x2_power, x2).as_str());
            let y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl y2:{}", y2).as_str());

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

**File:** program/src/processor.rs (L263-280)
```rust
            } else {
                delta_x = 0;
                delta_y = 0;
            }
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

        Ok((delta_x, delta_y))
```

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

**File:** program/src/processor.rs (L1818-1841)
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
        amm.recent_epoch = Clock::get()?.epoch;
        Ok(())
    }
```
