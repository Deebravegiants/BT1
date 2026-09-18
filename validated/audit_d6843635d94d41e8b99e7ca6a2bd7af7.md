## Analysis

This maps to the same bug class as the `DropBox` report: a stateful "remaining/tracked" value is derived using integer-truncating arithmetic and later re-checked against a live-computed value, and once the drift makes the check fail, the legitimate operation reverts unconditionally — permanently freezing user funds until a privileged intervention.

In Raydium, the equivalent invariant is enforced in `Processor::calc_take_pnl`, which is called from both `process_deposit` and `process_withdraw` (the two unprivileged LP-facing paths).

### Title
Precision-loss in decimal normalization causes `calc_take_pnl`'s invariant check to permanently revert `Deposit`/`Withdraw`, freezing LP funds - ([File: program/src/processor.rs])

### Summary
`Calculator::normalize_decimal_v2` / `restore_decimal` use floor (`checked_div`) truncation when converting token amounts between native decimals and the internal `sys_decimal_value` scale. `target_orders.calc_pnl_x` / `calc_pnl_y` are persisted using these truncated, rounded-down values after every `Deposit` and `Withdraw`. `calc_take_pnl` then requires the freshly recomputed current invariant (`total_pc_without_take_pnl * total_coin_without_take_pnl`) to be `>=` the previously stored, rounding-degraded invariant (`calc_pnl_x * calc_pnl_y`), or it returns `AmmError::CalcPnlError`. Because rounding always moves state downward and is applied repeatedly on every LP action, the stored invariant can end up larger than what the live vault balances can reproduce, causing this check to fail permanently on all future deposits and withdrawals (except the privileged `WithdrawOnly` bypass).

### Finding Description
The invariant check lives in `calc_take_pnl`: [1](#0-0) 

If this fails, the function hard-reverts with `CalcPnlError`: [2](#0-1) 

`calc_take_pnl` is called unconditionally in `process_deposit`: [3](#0-2) 

and conditionally in `process_withdraw` (skipped only when `amm.status == AmmStatus::WithdrawOnly`, a privileged admin-controlled status): [4](#0-3) 

The inputs `x1`/`y1` used for the "current" side of the check are computed via `normalize_decimal_v2`, which floors: [5](#0-4) 

`target_orders.calc_pnl_x`/`calc_pnl_y` — the "last recorded" side of the check — are re-derived every deposit/withdraw from these same floor-rounded normalized values combined with `restore_decimal` (also a floor `checked_div`): [6](#0-5) [7](#0-6) [8](#0-7) 

Because every normalization/restoration step in this chain truncates rather than rounds, and this happens on *every* deposit and withdraw, the stored `calc_pnl_x * calc_pnl_y` value systematically decays more slowly (or drifts inconsistently) relative to what the live vault balances (`total_pc_without_take_pnl * total_coin_without_take_pnl`, computed fresh from vault token accounts each call) can reproduce. An attacker (or just organic usage) can drive this by repeatedly performing minimal deposit/withdraw cycles that maximize floor-rounding loss (e.g., choosing `max_coin_amount`/`max_pc_amount` at decimal boundaries where `restore_decimal(normalize_decimal_v2(x))` truncates away non-zero remainders). Once `pool_pc_amount * pool_coin_amount < calc_pnl_x * calc_pnl_y`, `calc_take_pnl` reverts with `CalcPnlError` on every subsequent call.

### Impact Explanation
Once triggered, this permanently blocks:
- `process_deposit` for any user (no bypass exists — `calc_take_pnl` is called unconditionally),
- `process_withdraw` for any user unless the pool owner separately sets `AmmStatus::WithdrawOnly` (a privileged, off-chain-triggered mitigation not available to a normal LP or swapper).

This freezes LP principal and any pending PnL for the pool indefinitely from a purely unprivileged transaction path, matching the "permanent freezing of user or LP funds" impact bar. Swaps (`process_swap_base_in`/`_out` and their `_v2` variants) are unaffected since they don't call `calc_take_pnl`, but liquidity providers cannot deposit or withdraw normally.

### Likelihood Explanation
Reachable purely through the standard `Deposit`/`Withdraw` instructions with attacker-chosen `max_coin_amount`/`max_pc_amount`/`withdraw.amount` — no special accounts, signers, or admin privileges required. The likelihood of naturally drifting into this state depends on decimal configuration (`pc_decimals`, `coin_decimals`, `sys_decimal_value`) and volume of deposit/withdraw cycles, but an attacker can accelerate it deliberately by repeatedly performing deposit/withdraw pairs sized to maximize truncation loss each round, since `calc_pnl_x`/`calc_pnl_y` accumulate rounding error monotonically.

### Recommendation
- Avoid persisting a strict `>=` invariant check derived from lossy, floor-rounded decimal conversions as a hard revert condition on the unprivileged deposit/withdraw path.
- Either use round-nearest (or round in the direction that keeps the invariant conservative in the same direction consistently) in `normalize_decimal_v2`/`restore_decimal`, or replace the hard `CalcPnlError` revert with a saturating/clamping fallback (e.g., treat `pc_pnl_amount`/`coin_pnl_amount` as `0` when the invariant would otherwise go negative, similar to the existing `else { delta_x = 0; delta_y = 0; }` branch) so ordinary deposits/withdraws can never be permanently blocked by pnl-accounting rounding drift.
- Provide an unprivileged recovery path (equivalent to fixing the `remainingBoxesAmountCache` check in the referenced report) instead of relying solely on an admin-only `WithdrawOnly` status change.

### Proof of Concept
1. Initialize a pool via `Initialize2` with `pc_decimals`/`coin_decimals` set higher than `sys_decimal_value`'s decimal precision (e.g., 9-decimal tokens with `sys_decimal_value = 10^6`), so `normalize_decimal_v2`/`restore_decimal` truncate a non-trivial remainder on every call.
2. Repeatedly call `Deposit` then `Withdraw` (unprivileged) with amounts chosen so that `deduct_pc_amount`/`deduct_coin_amount`/`coin_amount`/`pc_amount` are not exact multiples of `10^(native_decimals - sys_decimal_digits)`, forcing `restore_decimal(normalize_decimal_v2(...))` to lose the remainder each round — this monotonically inflates `target_orders.calc_pnl_x * calc_pnl_y` relative to what live vault balances can reproduce.
3. After sufficient rounds, call `Deposit` (or `Withdraw` while `amm.status != WithdrawOnly`) again: `calc_take_pnl`'s check `pool_pc_amount.checked_mul(pool_coin_amount) >= calc_pc_amount.checked_mul(calc_coin_amount)` at `program/src/processor.rs:190-192` fails, and the instruction reverts with `AmmError::CalcPnlError` at `program/src/processor.rs:277`, permanently blocking further deposits and non-`WithdrawOnly` withdrawals for that pool.

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
