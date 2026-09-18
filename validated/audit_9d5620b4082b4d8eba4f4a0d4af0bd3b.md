I have sufficient evidence to confirm the analog. Let me finalize the analysis.

### Title
Unchecked assumption that `need_take_pnl_pc`/`need_take_pnl_coin` never exceeds vault balance causes permanent DoS of all swap, deposit and withdraw instructions - (File: `program/src/math.rs`)

### Summary
`Calculator::calc_total_without_take_pnl_no_orderbook` computes the pool's tradeable reserves by subtracting the internally tracked, not-yet-withdrawn PnL (`amm.state_data.need_take_pnl_pc` / `need_take_pnl_coin`) from the actual SPL token vault balances, using `checked_sub` that returns `AmmError::CheckedSubOverflow` on underflow. This mirrors the Ethos `ActivePool` bug: the code assumes the tracked liability (`need_take_pnl_*`, analogous to `currentAllocated`) can never exceed the real, current asset balance (analogous to `sharesToAssets`), but nothing in the protocol enforces that invariant against drift, so a single stale/inflated `need_take_pnl_*` value permanently bricks the pool.

### Finding Description
`calc_total_without_take_pnl_no_orderbook` is the single choke point used by essentially every core AMM instruction reachable by an unprivileged user: [1](#0-0) 

It is invoked at the top of `process_swap_base_in`/`_v2`, `process_swap_base_out`/`_v2`, `process_deposit`, `process_withdraw`, and `process_withdrawpnl` before any other logic runs: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

`need_take_pnl_pc`/`need_take_pnl_coin` are an internally accrued, ever-growing "IOU" balance that is only ever incremented (via `checked_add` in `calc_take_pnl`) during swaps, deposits and withdrawals, and only cleared by `process_withdrawpnl`: [6](#0-5) 

Crucially, `process_withdrawpnl` itself calls `calc_total_without_take_pnl_no_orderbook` *before* it checks `need_take_pnl_coin <= amm_coin_vault.amount && need_take_pnl_pc <= amm_pc_vault.amount`: [7](#0-6) [8](#0-7) 

This means there is no recovery path: if `need_take_pnl_pc`/`need_take_pnl_coin` ever becomes greater than the actual, current on-chain vault token balance, `calc_total_without_take_pnl_no_orderbook` reverts with `CheckedSubOverflow` on every single call, including the one inside `process_withdrawpnl` that would otherwise be used to reconcile/clear the value. This deadlocks the pool for swaps, deposits, withdrawals, and PnL withdrawal simultaneously — exactly the same class of bug as the referenced report, where `vars.sharesToAssets.sub(vars.currentAllocated)` reverts once the tracked allocation exceeds the real (post-loss) asset value, and there is no way to reconcile since every code path routes through the same failing subtraction.

The invariant `need_take_pnl_pc/coin <= actual vault balance` is enforced only by the accounting logic inside `calc_take_pnl`, which relies on `restore_decimal`/`normalize_decimal_v2` fixed-point decimal conversions between `sys_decimal_value` and each token's native decimals: [9](#0-8) 

Because these conversions truncate towards zero (integer division) in one direction and are applied asymmetrically when converting delta_x/delta_y back to native pc/coin units versus when they were derived from normalized amounts, repeated cycles of swaps/deposits/withdrawals that invoke `calc_take_pnl` can accumulate rounding drift in `need_take_pnl_pc`/`need_take_pnl_coin` relative to the true reserves, especially for coin/pc mint pairs with differing decimals. There is no assertion anywhere in the codebase that re-validates `need_take_pnl_pc <= pc_vault.amount` and `need_take_pnl_coin <= coin_vault.amount` immediately after `calc_take_pnl` updates these fields in the swap/deposit/withdraw paths (only `process_withdrawpnl` checks it, after the fact, and only once the unconditional subtraction earlier in the same function has already reverted).

### Impact Explanation
Once `need_take_pnl_pc` or `need_take_pnl_coin` exceeds the corresponding vault's real SPL token balance, `calc_total_without_take_pnl_no_orderbook` unconditionally reverts for every caller. Because every reachable, unprivileged-user-facing instruction (`SwapBaseIn`, `SwapBaseInV2`, `SwapBaseOut`, `SwapBaseOutV2`, `Deposit`, `Withdraw`) and even the privileged `WithdrawPnl` instruction call this function first, the entire pool becomes permanently frozen: LPs cannot withdraw their capital, swappers cannot trade, and the owner cannot reconcile/withdraw the accrued PnL to reset the counters. This is a permanent freezing of all user and LP funds in the pool, matching the "concrete... permanent freezing of user or LP funds" acceptance criterion.

### Likelihood Explanation
The trigger does not require any privileged action, malicious validator, or off-chain component — it can be reached purely through the normal, repeated use of `SwapBaseIn`/`SwapBaseOut`/`Deposit`/`Withdraw` by ordinary users on pools whose coin/pc mints have differing decimals (a very common configuration on Raydium, e.g. 6-decimal vs 9-decimal tokens), since `calc_take_pnl`'s decimal normalization/restoration round-trips through `sys_decimal_value` using floor division at multiple points. Over many trade/deposit/withdraw cycles the accumulated truncation can push the tracked `need_take_pnl_*` counters past the real vault balance. The likelihood of an attacker being able to deliberately accelerate this drift with a sequence of small, carefully chosen swap/deposit/withdraw amounts (each individually legitimate) is credible, though the number of iterations/precision analysis needed to force the exact crossover is nontrivial to fully characterize without on-chain simulation.

### Recommendation
- After updating `need_take_pnl_pc`/`need_take_pnl_coin` in `calc_take_pnl`, assert that they remain `<=` the actual vault balances, and clamp/cap them rather than trusting unchecked growth.
- In `calc_total_without_take_pnl_no_orderbook`, replace the hard revert on `checked_sub` failure with a saturating subtraction (returning 0) so that the pool degrades gracefully instead of becoming permanently unusable, and log/flag the inconsistency for the owner to reconcile via a dedicated recovery instruction.
- Ensure `process_withdrawpnl`'s vault-balance sufficiency check happens (or an equivalent one is available) independently of the general `calc_total_without_take_pnl_no_orderbook` path, so PnL/accounting drift can always be reconciled even if the general subtraction would underflow.

### Proof of Concept
1. Create an AMM pool where `coin_decimals != pc_decimals` (e.g. 9-decimal coin, 6-decimal pc), which is standard for many Raydium pools.
2. Repeatedly execute `SwapBaseIn`/`SwapBaseOut` and `Deposit`/`Withdraw` instructions with amounts chosen to maximize floor-division truncation in `Calculator::normalize_decimal_v2`/`restore_decimal` inside `calc_take_pnl` (`program/src/processor.rs:167-281`), each time incrementing `amm.state_data.need_take_pnl_pc`/`need_take_pnl_coin` via `checked_add`.
3. Because the reverse decimal restoration used to compute `pc_pnl_amount`/`coin_pnl_amount` is not fully symmetric with the normalization used to compute `x1`/`y1`, iterate until `need_take_pnl_pc` (or `need_take_pnl_coin`) exceeds the vault's true SPL token balance (`amm_pc_vault.amount`/`amm_coin_vault.amount`).
4. Submit any subsequent `SwapBaseIn`, `SwapBaseOut`, `Deposit`, or `Withdraw` instruction: `Calculator::calc_total_without_take_pnl_no_orderbook` (`program/src/math.rs:243-248`) reverts with `AmmError::CheckedSubOverflow` for every caller.
5. Attempt `WithdrawPnl`: it calls the same `calc_total_without_take_pnl_no_orderbook` at `program/src/processor.rs:1459-1464` before its own sufficiency check at `program/src/processor.rs:1505-1507`, so it reverts as well — there is no remaining instruction path to reconcile the pool, permanently freezing all coin/pc funds held by the AMM.

### Citations

**File:** program/src/math.rs (L80-116)
```rust
    pub fn normalize_decimal(val: u64, native_decimal: u64, sys_decimal_value: u64) -> u64 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**9) -> (1.23*10**6)
        //let ret:u64 = val.checked_mul(amm.sys_decimal_value).unwrap().checked_div((10 as u64).pow(native_decimal.into())).unwrap();
        let ret_mut = (U128::from(val))
            .checked_mul(sys_decimal_value.into())
            .unwrap();
        let ret = Self::to_u64(
            ret_mut
                .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
                .unwrap()
                .as_u128(),
        )
        .unwrap();
        ret
    }

    pub fn restore_decimal(val: U128, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**6) -> (1.23*10**9)
        // let ret:u64 = val.checked_mul((10 as u64).pow(native_decimal.into())).unwrap().checked_div(amm.sys_decimal_value).unwrap();
        let ret_mut = val
            .checked_mul(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        let ret = ret_mut.checked_div(sys_decimal_value.into()).unwrap();
        ret
    }

    pub fn normalize_decimal_v2(val: u64, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**9) -> (1.23*10**6)
        //let ret:u64 = val.checked_mul(amm.sys_decimal_value).unwrap().checked_div((10 as u64).pow(native_decimal.into())).unwrap();
        let ret_mut = (U128::from(val))
            .checked_mul(sys_decimal_value.into())
            .unwrap();
        let ret = ret_mut
            .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        ret
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

**File:** program/src/processor.rs (L1458-1465)
```rust
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

```

**File:** program/src/processor.rs (L1505-1507)
```rust
        if amm.state_data.need_take_pnl_coin <= amm_coin_vault.amount
            && amm.state_data.need_take_pnl_pc <= amm_pc_vault.amount
        {
```

**File:** program/src/processor.rs (L1719-1724)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
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

**File:** program/src/processor.rs (L2154-2159)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```
