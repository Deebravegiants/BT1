### Title
Permanent DoS of Deposit/Withdraw via `CalcPnlError` from decimal-rounding drift between `calc_pnl_x/y` and pool reserves - (File: `program/src/processor.rs`)

### Summary
`calc_take_pnl`, invoked on every `Deposit`, non-`WithdrawOnly` `Withdraw`, and `WithdrawPnl`, requires `total_pc * total_coin >= restore_decimal(calc_pnl_x) * restore_decimal(calc_pnl_y)` or it hard-fails the whole instruction with `AmmError::CalcPnlError`. Because `calc_pnl_x`/`calc_pnl_y` are maintained in a different fixed-point scale (`sys_decimal_value`) than the raw token amounts, and the conversions between the two use truncating integer division (`normalize_decimal_v2`/`restore_decimal`), repeated deposit/withdraw cycles by an ordinary LP can drift `calc_pnl_x * calc_pnl_y` above the true pool invariant, permanently tripping this check for all normal-path Deposit/Withdraw calls.

### Finding Description
`calc_take_pnl` gates state updates with: [1](#0-0) 
comparing raw pool reserves against `restore_decimal(target.calc_pnl_x/y, ...)`, which itself is derived from a prior `normalize_decimal_v2` truncation: [2](#0-1) 

On every `Deposit`, `target_orders.calc_pnl_x`/`calc_pnl_y` are recomputed as `x1 + normalize_decimal_v2(deduct_amount) - delta_x` (and symmetrically for withdraw): [3](#0-2) 
and on `Withdraw`: [4](#0-3) 

Both `Deposit` and non-`WithdrawOnly` `Withdraw` unconditionally call `calc_take_pnl`, and any failure there (the `else` branch below) aborts the instruction with no way for an ordinary account to reset `calc_pnl_x`/`calc_pnl_y`: [5](#0-4) 

Notably, `SwapBaseIn`/`SwapBaseOut`/`SwapBaseInV2`/`SwapBaseOutV2` never call `calc_take_pnl` at all — they only use `calc_total_without_take_pnl_no_orderbook` — so swaps remain functional even after this state is corrupted: [6](#0-5) 

Because `normalize_decimal_v2`/`restore_decimal` floor-divide on every deposit/withdraw, an attacker who repeatedly deposits and withdraws small amounts (fully permissionless, any LP can call these) can accumulate rounding error such that `restore_decimal(calc_pnl_x) * restore_decimal(calc_pnl_y)` creeps above the actual `total_pc * total_coin`. Once that inequality flips, every subsequent `Deposit` and normal `Withdraw` (and `WithdrawPnl`) call permanently fails with `CalcPnlError`. The only bypass is `Withdraw` while `amm.status == WithdrawOnly`: [7](#0-6) 
which requires a privileged `SetParams` call by the pool's admin — out of reach for a normal LP, and not something the protocol does automatically.

### Impact Explanation
Once triggered, LPs lose the ability to deposit into or withdraw normally from the pool, and the protocol cannot collect/withdraw accrued PnL, effectively freezing LP liquidity-management functions for that pool until an admin manually intervenes (setting `WithdrawOnly`, which itself requires a privileged signer and only unlocks Withdraw). This matches a "hang/crash → permanent unavailability" analog of the CVE, applied to core AMM liquidity management rather than the trading path.

### Likelihood Explanation
Any unprivileged LP or pool creator can call `Deposit`/`Withdraw` with attacker-chosen (small) amounts repeatedly, using only default, permissionless instructions. Because the drift depends on the accumulated floor/ceiling rounding across many small transactions relative to `sys_decimal_value` and token decimals, achieving the flip is mechanically straightforward but requires multiple iterations rather than a single call, and the amount of drift needed depends on pool decimals/`sys_decimal_value` — this is not a single-shot exploit for every pool configuration, so likelihood is assessed as Medium rather than High.

### Recommendation
Store `calc_pnl_x`/`calc_pnl_y` and pool reserves in a single consistent unit to avoid repeated truncating conversions, or track and periodically correct accumulated rounding remainder from `normalize_decimal_v2`/`restore_decimal`. Additionally, avoid hard-failing `Deposit`/`Withdraw`/`WithdrawPnl` entirely on the `calc_take_pnl` invariant violation — instead clamp/skip the PnL-taking step (as already done for `WithdrawOnly`) so liquidity operations remain available even if the PnL bookkeeping momentarily disagrees due to rounding.

### Proof of Concept
1. Initialize a pool via `Initialize2` with token decimals that don't evenly divide `sys_decimal_value` (e.g., coin_decimals=9, pc_decimals=6, `sys_decimal_value=10^6`), so `normalize_decimal_v2`/`restore_decimal` conversions are lossy.
2. As the LP, repeatedly call `Deposit` then `Withdraw` for small, non-round amounts in a loop (each in its own transaction), letting `target_orders.calc_pnl_x`/`calc_pnl_y` accumulate via `processor.rs:1352-1371` and the withdraw equivalent at `processor.rs:1719-1749`.
3. After enough iterations, `restore_decimal(calc_pnl_x, ...) * restore_decimal(calc_pnl_y, ...)` exceeds `total_pc_without_take_pnl * total_coin_without_take_pnl`, causing `calc_take_pnl` (`processor.rs:188-192`) to hit the `else` branch and return `AmmError::CalcPnlError` (`processor.rs:267-278`).
4. From this point, all subsequent `Deposit`, normal `Withdraw`, and `WithdrawPnl` calls fail deterministically, while `SwapBaseIn`/`SwapBaseOut` continue to work (`processor.rs:1940-1946`), confirming the liquidity-management functions are selectively and permanently frozen absent admin intervention.

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

**File:** program/src/processor.rs (L1719-1749)
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

**File:** program/src/processor.rs (L1940-1946)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

```

**File:** program/src/math.rs (L80-104)
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
```
