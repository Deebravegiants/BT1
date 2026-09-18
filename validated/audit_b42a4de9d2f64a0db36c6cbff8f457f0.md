### Title
Unchecked division by zero-normalized reserve in `calc_x_power` freezes Withdraw/WithdrawPnl - (File: program/src/math.rs)

### Summary
`Calculator::calc_x_power()` performs `checked_div(current_y).unwrap()` with no protection against a zero divisor [1](#0-0) . The `current_y` value fed into this function is the normalized pool reserve produced by `Calculator::normalize_decimal_v2()`, which truncates to `0` whenever the raw token balance is small relative to `10^native_decimal / sys_decimal_value` [2](#0-1) . An unprivileged swapper can drive a pool's coin (or pc) reserve down to a raw balance below this truncation threshold using ordinary `SwapBaseIn`/`SwapBaseOut` calls, because the only floor check in those handlers is that the outgoing amount must leave the vault non-zero, not above the decimal-normalization threshold [3](#0-2) . Once the reserve is in this state, any subsequent call to `Deposit`, `Withdraw`, or `WithdrawPnl` — which all invoke `Processor::calc_take_pnl` → `Calculator::calc_x_power` — panics and aborts, because ImageMagick's analogous fix (`PerceptibleReciprocal`-style zero guard) is absent here.

### Finding Description
`calc_take_pnl` is called from `process_deposit`, `process_withdraw`, and `process_withdrawpnl` [4](#0-3) [5](#0-4) . Inside it, the pool's current (post-drain) reserves `x1`/`y1` are computed via `Calculator::normalize_decimal_v2(total_..._without_take_pnl, decimals, sys_decimal_value)` and then passed as `current_x`/`current_y` into `Calculator::calc_x_power` [6](#0-5) .

`normalize_decimal_v2` computes `val * sys_decimal_value / 10^native_decimal` using integer division [2](#0-1) . For a typical SPL token with 9 decimals and the program's `sys_decimal_value` fixed at `10^6` (as used throughout the test fixtures, e.g. `amm.initialize(0, 0, 2, 9, 1000000, 1)` [7](#0-6) ), any raw balance below `1000` (i.e. `10^(9-6)`) normalizes to exactly `0`.

`calc_x_power` then computes:
```
x_power = last_x * last_y * current_x / current_y
```
using `.checked_div(current_y).unwrap()` [8](#0-7) . When `current_y` (i.e. `y1`, the normalized coin reserve) is `0`, `checked_div` returns `None` and `.unwrap()` panics, aborting the transaction with a runtime panic rather than a graceful error.

Reachability: the only guard preventing a swap from draining a vault is the strict inequality check `swap_amount_out >= total_pc_without_take_pnl` / `total_coin_without_take_pnl` in `process_swap_base_in`/`process_swap_base_out` (and their V2 counterparts) [3](#0-2) [9](#0-8) , which only guarantees the reserve stays `>= 1` raw unit — far below the `1000`-unit normalization threshold for a 9-decimal token. Nothing in the swap path calls `calc_take_pnl`, so an attacker can freely push a reserve into this danger zone using only `SwapBaseIn`/`SwapBaseOut` with attacker-chosen `amount_in`/`amount_out`, both fully swapper-controlled instruction arguments.

### Impact Explanation
Once a pool's coin or pc reserve is driven below the decimal-normalization threshold, every subsequent `Withdraw` and `WithdrawPnl` call (and `Deposit`, which also calls `calc_take_pnl`) panics and reverts. This means LPs cannot withdraw their liquidity from the pool while it remains in this state, effectively freezing LP funds — the pool becomes usable only for swaps (which don't trigger `calc_take_pnl`) but not for the accounting/PNL-taking path that both deposit and withdraw depend on. This matches the CVSS/impact profile of the reference disclosure (availability impact from unguarded division), translated here into a fund-freezing effect on Solana rather than a service crash, since Solana transactions revert on panic rather than crashing the validator.

### Likelihood Explanation
Likelihood is high for pools with low-liquidity or thinly-traded reserves and tokens with more decimals than `sys_decimal_value`'s implicit precision (`10^6`), which is the common configuration for most SPL tokens (9 decimals). Any single unprivileged swapper, using only publicly documented `SwapBaseIn`/`SwapBaseOut` instructions with attacker-chosen `amount_in`/`amount_out`, can push a reserve into the vulnerable range in one transaction, with no special privileges required.

### Recommendation
- Add an explicit zero-check (or use a `checked_div` that maps `None` to a proper `AmmError` instead of `.unwrap()`) in `Calculator::calc_x_power` before dividing by `current_y`.
- Additionally, harden `normalize_decimal_v2`/`restore_decimal` to reject or safely propagate the case where truncation produces `0` for a nonzero input, and consider enforcing a minimum reserve size in swap handlers (analogous to `PerceptibleReciprocal` in the referenced ImageMagick fix) so reserves can never be swapped below the decimal-normalization resolution.

### Proof of Concept
1. Create a pool via `Initialize2` with a coin mint of 9 decimals and any pc mint, with `sys_decimal_value = 10^6` (default program behavior).
2. As an unprivileged swapper, repeatedly call `SwapBaseIn`/`SwapBaseOut` (PC→Coin direction) with `amount_out` chosen such that `total_coin_without_take_pnl` after the swap is left at some value `< 1000` raw units (e.g., `1`), which is permitted since the only check is `swap_amount_out >= total_coin_without_take_pnl` [9](#0-8) .
3. Call `Withdraw` (or `WithdrawPnl`/`Deposit`). `process_withdraw` computes `y1 = Calculator::normalize_decimal_v2(total_coin_without_take_pnl, amm.coin_decimals, amm.sys_decimal_value)` [10](#0-9) , which truncates to `0`.
4. `Self::calc_take_pnl(..., y1.as_u128().into())` is invoked [11](#0-10) , calling `Calculator::calc_x_power(..., current_y=0)`, which panics on `.checked_div(current_y).unwrap()` [8](#0-7) , causing the `Withdraw` transaction to abort and LP funds to remain locked in the pool.

### Citations

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

**File:** program/src/processor.rs (L199-204)
```rust
            let x2_power = Calculator::calc_x_power(
                target.calc_pnl_x.into(),
                target.calc_pnl_y.into(),
                x1,
                y1,
            );
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

**File:** program/src/processor.rs (L1494-1501)
```rust
        // calc and update pnl
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
```

**File:** program/src/processor.rs (L1726-1735)
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
```

**File:** program/src/processor.rs (L1741-1748)
```rust
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
```

**File:** program/src/processor.rs (L2000-2004)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap_amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/processor.rs (L2212-2216)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/processor.rs (L3222-3223)
```rust
        let mut amm = AmmInfo::default();
        amm.initialize(0, 0, 2, 9, 1000000, 1).unwrap();
```
