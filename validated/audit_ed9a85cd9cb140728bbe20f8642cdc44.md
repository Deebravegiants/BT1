## Analysis

The Sherlock report's bug class is: **unvalidated numeric parameters cause integer‑division truncation, making a supposedly variable on‑chain value effectively frozen/degenerate** (`totalSteps` floors to 1, so price never moves).

The closest reachable analog in this program is the decimal‑normalization math used throughout swap/deposit/withdraw/pnl accounting, `Calculator::normalize_decimal_v2` / `Calculator::restore_decimal`, which perform `val * sys_decimal_value / 10^native_decimal`. `native_decimal` is taken directly from the **coin/pc SPL mint's `decimals` field**, which is fully attacker-controlled at `Initialize2` time (any user can create a pool with a token mint they minted themselves, choosing an arbitrary `decimals` value up to `u8::MAX`), while `sys_decimal_value` is a fixed constant.

### Title
Attacker-controlled mint decimals in `normalize_decimal_v2`/`restore_decimal` can truncate pool balances to zero, corrupting PnL accounting reachable from unprivileged Deposit/Withdraw/Swap - (File: `program/src/math.rs`, `program/src/processor.rs`)

### Summary
`Calculator::normalize_decimal_v2` and `Calculator::restore_decimal` compute `val * sys_decimal_value / 10^native_decimal` with no bound on `native_decimal`, which is sourced from the coin/pc mint's `decimals` field set when an unprivileged user creates a pool via `Initialize2`. As in the reported Dutch-auction bug (unvalidated `stepSize_` making integer division collapse to a constant/degenerate result), an attacker who mints a token with a sufficiently large `decimals` value can make `10^native_decimal` dominate the numerator, causing the normalized (or restored) balance to truncate to `0`.

### Finding Description [1](#0-0) [2](#0-1) 

These normalization helpers are invoked with `amm.coin_decimals` / `amm.pc_decimals`, which are set at pool creation directly from the coin/pc mint accounts supplied to `Initialize2` — accounts fully chosen by the transaction's signer: [3](#0-2) [4](#0-3) 

No check exists anywhere in `process_initialize2` bounding `coin_mint.decimals`/`pc_mint.decimals` to a sane range (e.g., ≤ 9). Since `sys_decimal_value` is a small fixed constant (commented as `10**6`), a mint with a large `decimals` value makes `10^native_decimal` overwhelm `val * sys_decimal_value`, and the `checked_div` floors the result to `0`, exactly mirroring the reported root cause (unvalidated divisor/exponent parameter causing integer-division truncation of an economically important value).

These normalized `x1`/`y1` values feed directly into `calc_take_pnl`, which is executed on the unprivileged `Deposit`, `Withdraw`, and legacy `SwapBaseIn`/`SwapBaseOut` paths: [5](#0-4) [6](#0-5) 

If `x1` or `y1` truncates to `0`, the pnl-take calculation (`last_k`, `current_price`, `x_after_take_pnl`, `y_after_take_pnl`) degenerates, and `total_pc_without_take_pnl` / `total_coin_without_take_pnl` — the values used as the constant-product reserves for every subsequent swap — become corrupted/insolvent relative to actual vault balances.

### Impact Explanation
A corrupted `need_take_pnl_pc`/`need_take_pnl_coin` state breaks the invariant used by `swap_token_amount_base_in`/`swap_token_amount_base_out` for every swapper against that pool, and by the LP mint/burn math in Deposit/Withdraw (`InvariantToken`, `InvariantPool`), leading to insolvent pool accounting: swappers or LPs can receive amounts inconsistent with real reserves, i.e., unbacked value extraction or fund freezing for the pool's other participants.

### Likelihood Explanation
Exploitation requires only steps reachable in a single flow with attacker-chosen accounts/data: mint a custom SPL token with an inflated `decimals` value, call `Initialize2` to create a pool with it, then call `Deposit`/`Withdraw`/legacy `SwapBaseIn`/`SwapBaseOut` — no privileged signer or off-chain component is needed.

### Recommendation
Bound `coin_mint.decimals`/`pc_mint.decimals` (e.g., require `decimals <= 9` or otherwise ensure `10^decimals <= sys_decimal_value` headroom) in `process_initialize2`, and add an explicit check in `normalize_decimal_v2`/`restore_decimal` that the normalized result is non-zero (or fails loudly) whenever the input amount was non-zero, rather than silently truncating.

### Proof of Concept
1. Attacker creates a new SPL mint (`coin_mint`) with `decimals = 19` (or another value large enough that `10^decimals` exceeds `coin_amount * sys_decimal_value`).
2. Attacker calls `Initialize2` supplying this mint alongside a normal `pc_mint`, funding coin/pc vaults with modest but nonzero amounts satisfying `InitLpAmountTooLess` checks ( [7](#0-6) ).
3. `amm.coin_decimals` is now `19`; every subsequent call to `Calculator::normalize_decimal_v2(coin_amount, 19, sys_decimal_value)` truncates to `0` ( [1](#0-0) ).
4. Attacker calls `Deposit` or the legacy `SwapBaseIn`, triggering `calc_take_pnl` with a zeroed `y1` ( [6](#0-5) ), corrupting the pool's `total_*_without_take_pnl` reserve accounting used for all future swaps/LP math.

**Caveat**: I could not fully verify the exact downstream arithmetic in `calc_take_pnl` beyond line 190 (the file segment returned was truncated), so the precise numeric consequence (e.g., whether `delta_x`/`delta_y` become negative-clamped, saturate, or panic) is not fully confirmed from the indexed code; a full review of `program/src/processor.rs` lines ~190–260 (`calc_take_pnl` body) in a Devin session would be needed to confirm the exact failure mode (panic/revert vs. silent insolvency) before treating this as a certain High/Critical finding.

### Citations

**File:** program/src/math.rs (L96-104)
```rust
    pub fn restore_decimal(val: U128, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**6) -> (1.23*10**9)
        // let ret:u64 = val.checked_mul((10 as u64).pow(native_decimal.into())).unwrap().checked_div(amm.sys_decimal_value).unwrap();
        let ret_mut = val
            .checked_mul(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        let ret = ret_mut.checked_div(sys_decimal_value.into()).unwrap();
        ret
    }
```

**File:** program/src/math.rs (L106-116)
```rust
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

**File:** program/src/processor.rs (L159-190)
```rust
    /// The Detailed calculation of pnl
    /// 1. calc last_k witch dose not take pnl: last_k = calc_pnl_x * calc_pnl_y;
    /// 2. calc current price: current_price = current_x / current_y;
    /// 3. calc x after take pnl: x_after_take_pnl = sqrt(last_k * current_price);
    /// 4. calc y after take pnl: y_after_take_pnl = x_after_take_pnl / current_price;
    ///                           y_after_take_pnl = x_after_take_pnl * current_y / current_x;
    /// 5. calc pnl_x & pnl_y:  pnl_x = current_x - x_after_take_pnl;
    ///                         pnl_y = current_y - y_after_take_pnl;
    pub fn calc_take_pnl(
        target: &TargetOrders,
        amm: &mut AmmInfo,
        total_pc_without_take_pnl: &mut u64,
        total_coin_without_take_pnl: &mut u64,
        x1: U256,
        y1: U256,
    ) -> Result<(u128, u128), ProgramError> {
        // calc pnl
        let mut delta_x: u128;
        let mut delta_y: u128;
        let calc_pc_amount = Calculator::restore_decimal(
            target.calc_pnl_x.into(),
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let calc_coin_amount = Calculator::restore_decimal(
            target.calc_pnl_y.into(),
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
```

**File:** program/src/processor.rs (L908-917)
```rust
        let liquidity = Calculator::to_u64(
            U128::from(amm_pc_vault.amount)
                .checked_mul(amm_coin_vault.amount.into())
                .unwrap()
                .integer_sqrt()
                .as_u128(),
        )?;
        let user_lp_amount = liquidity
            .checked_sub((10u64).checked_pow(lp_mint.decimals.into()).unwrap())
            .ok_or(AmmError::InitLpAmountTooLess)?;
```

**File:** program/src/processor.rs (L930-938)
```rust

        amm.initialize(
            init.nonce,
            init.open_time,
            coin_mint.decimals,
            pc_mint.decimals,
            0,
            0,
        )?;
```

**File:** program/src/processor.rs (L950-959)
```rust
        let x = Calculator::normalize_decimal_v2(
            amm_pc_vault.amount,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y = Calculator::normalize_decimal_v2(
            amm_coin_vault.amount,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
```

**File:** program/src/processor.rs (L1155-1173)
```rust
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
