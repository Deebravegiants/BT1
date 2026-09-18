### Title
`calc_take_pnl` reverts on rounding-induced k-invariant drift, permanently blocking `Deposit`/`Withdraw` — ([File: program/src/processor.rs])

### Summary
`Processor::calc_take_pnl` gates every profit-and-loss calculation behind a strict invariant check that compares the *current* pool value (`pool_pc_amount * pool_coin_amount`) against the *cached* baseline stored in `TargetOrders` (`calc_pc_amount * calc_coin_amount`). If the current value ever falls even slightly below the cached baseline — which is achievable purely through repeated integer-truncation in the decimal-normalization round trips used by every state-mutating instruction — the function unconditionally returns `AmmError::CalcPnlError`, and since `calc_take_pnl` is invoked from `process_deposit` and `process_withdraw` (both callable by any unprivileged LP), this turns into a permanent denial of service for the pool.

### Finding Description
`calc_take_pnl` computes:

```
pool_pc_amount = total_pc_without_take_pnl        // current, native decimals
pool_coin_amount = total_coin_without_take_pnl
calc_pc_amount = restore_decimal(target.calc_pnl_x, pc_decimals, sys_decimal_value)   // cached baseline
calc_coin_amount = restore_decimal(target.calc_pnl_y, coin_decimals, sys_decimal_value)

if pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount {
    ... proceed ...
} else {
    return Err(AmmError::CalcPnlError);   // hard revert, no recovery
}
``` [1](#0-0) [2](#0-1) 

`target_orders.calc_pnl_x`/`calc_pnl_y` are re-derived after every `Deposit`/`Withdraw`/`WithdrawPnl` using `normalize_decimal_v2` (native → sys-decimal, floor division) and `restore_decimal` (sys-decimal → native, floor division): [3](#0-2) 

Because both conversions floor-divide, every deposit/withdraw that updates the cached baseline (`target_orders.calc_pnl_x`/`calc_pnl_y`, see `process_deposit`) accumulates a small downward truncation bias: [4](#0-3) 

and the same pattern repeats in `process_withdraw`: [5](#0-4) 

Over many `Deposit`/`Withdraw` calls (fully attacker-controllable — an unprivileged user can force many small deposits/withdrawals, or such rounding may organically occur for pools with divergent `pc_decimals`/`coin_decimals`, e.g. the project's own test uses `pc_decimals=2, coin_decimals=9`), the recorded `calc_pnl_x * calc_pnl_y` baseline can end up numerically higher, relative to the true pool reserves, than the actual current `x1 * y1` once re-derived through the lossy `restore_decimal`/`normalize_decimal_v2` round trip. When that happens, the guard `pool_pc_amount*pool_coin_amount >= calc_pc_amount*calc_coin_amount` fails and `calc_take_pnl` returns `Err(AmmError::CalcPnlError)`.

This exactly mirrors the referenced Olympus bug class: an accounting/rounding fault in a per-user/per-pool running-total calculation causes a deterministic revert path that blocks legitimate operations rather than silently mis-accounting — a faulty-math-induced Denial of Service.

### Impact Explanation
Once the invariant check fails for a pool, **every subsequent `Deposit` and `Withdraw` instruction reverts**, because both call `calc_take_pnl` unconditionally (except when `amm.status == WithdrawOnly`, which is not the default operating state and requires privileged `SetParams`): [6](#0-5) [7](#0-6) 

This freezes LP withdrawals and new deposits for the affected pool — a permanent freezing of user/LP funds until a privileged admin manually intervenes (e.g., by setting `WithdrawOnly` status via `SetParams`, which itself only re-enables `Withdraw`, not `Deposit`, and does not fix the underlying stuck accounting). This satisfies the "permanent freezing of user or LP funds" acceptance criterion.

### Likelihood Explanation
This is reachable from a single unprivileged transaction stream: repeatedly calling `Deposit` and `Withdraw` (both public instructions with no special permission) is sufficient to accumulate truncation drift in `target_orders.calc_pnl_x`/`calc_pnl_y` relative to the true reserves, especially for pools with large decimal disparities between `coin_decimals` and `pc_decimals` (common for real token pairs, e.g. 6 vs 9, or 2 vs 9 as used in the repo's own precision test `test_calc_pnl_precision`). No special build flags, validator behavior, or leaked keys are required.

### Recommendation
Avoid a hard revert path driven purely by rounding noise:
- Replace the strict `>=` invariant rejection with a tolerance-based check, or clamp `calc_pc_amount`/`calc_coin_amount` to the current pool amounts before comparing, instead of aborting the whole instruction.
- Alternatively, recompute/re-anchor `target_orders.calc_pnl_x`/`calc_pnl_y` from the *actual* current native reserves at the start of `calc_take_pnl` rather than compounding normalize/restore round trips across many operations, eliminating cumulative truncation drift.
- Ensure `Deposit`/`Withdraw` cannot permanently fail due to this invariant; if the invariant genuinely cannot be satisfied, degrade gracefully (e.g., skip pnl extraction for that call) instead of returning `AmmError::CalcPnlError` and blocking the whole transaction.

### Proof of Concept
1. Initialize a pool with divergent decimals (e.g., `pc_decimals = 2`, `coin_decimals = 9`, matching the repo's own `test_calc_pnl_precision` setup) via `Initialize2`.
2. As any unprivileged LP, repeatedly call `Deposit` followed by `Withdraw` with amounts chosen to maximize floor-division loss in `normalize_decimal_v2`/`restore_decimal` on each pass (small deposit amounts relative to `sys_decimal_value` scale exacerbate truncation).
3. Each `Deposit`/`Withdraw` re-derives `target_orders.calc_pnl_x`/`calc_pnl_y` via the lossy round trip shown at `process_deposit` (lines 1352-1371) and `process_withdraw` (lines 1818-1838); the cached baseline compounds truncation error relative to real reserves.
4. After a sufficient number of iterations, submit another `Deposit`/`Withdraw`; `calc_take_pnl`'s guard at `processor.rs:190-192` now evaluates false, and the instruction reverts with `AmmError::CalcPnlError` (`processor.rs:277`), permanently blocking further deposits and withdrawals for the pool until a privileged fix is applied.

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

**File:** program/src/processor.rs (L1165-1173)
```rust
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

**File:** program/src/math.rs (L96-116)
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
