### Title
Unchecked arithmetic panic in `calc_take_pnl` reachable from `Deposit`/`Withdraw` causes permanent, repeatable pool-wide DOS - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` is invoked on every unprivileged `Deposit` and `Withdraw` instruction (and on `WithdrawPnl`) to reconcile the AMM's accrued PnL against the live pool balances [1](#0-0) . Inside this routine, several intermediate values are subtracted with a bare `.unwrap()` instead of returning a graceful error, most notably `x1.checked_sub(x2).unwrap()` and `y1.checked_sub(y2).unwrap()` [2](#0-1) . Because the gate that precedes this computation is evaluated in *native, unnormalized* token units while `x2`/`y2` are derived from *decimal-normalized* values that pass through truncating integer division (`normalize_decimal_v2` / `restore_decimal`) and an integer square root, the two representations of the invariant can disagree by rounding, allowing `x2 > x1` (or `y2 > y1`) even though the outer guard `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount` passed [3](#0-2) . When that happens the `unwrap()` panics and aborts the transaction.

### Finding Description
`calc_take_pnl` computes a rebalanced invariant point `(x2, y2)` from the AMM's stored `target.calc_pnl_x` / `target.calc_pnl_y` (already normalized to `sys_decimal_value`) and the current normalized pool totals `x1`, `y1` [4](#0-3) . `x1`/`y1` are produced by `Calculator::normalize_decimal_v2`, which performs a truncating `checked_div` when rescaling native token amounts (9/6/etc. decimals) down to the internal `sys_decimal_value` [5](#0-4) . `x2` is then computed via `calc_x_power` (itself a chain of `checked_mul`/`checked_div` in u256) followed by `integer_sqrt()` [6](#0-5) .

The precondition check that gates entry into this block compares *native* vault amounts (`pool_pc_amount`, `pool_coin_amount`, both `u64` converted via `U128::from`) against `calc_pc_amount`/`calc_coin_amount`, which are `target.calc_pnl_x`/`calc_pnl_y` restored back to native units via `Calculator::restore_decimal` [7](#0-6) . Because normalization/restoration round-trips through integer truncation, the native-unit check and the normalized-unit computation of `x2`/`y2` are not guaranteed to be consistent for all vault balances — an attacker who controls the exact `Deposit`/`Withdraw` amounts (and therefore the exact resulting vault balances) can steer the pool into a state where the native-unit gate passes but the normalized-space `x2 > x1` or `y2 > y1`, causing the subsequent `.unwrap()` on `checked_sub` to panic [8](#0-7) .

`calc_take_pnl` is called from `process_deposit` (any LP), `process_withdraw` (any LP), and `process_withdrawpnl`; the first two require no special privilege beyond owning tokens and signing the standard `Deposit`/`Withdraw` instruction accounts [9](#0-8) . Once `target.calc_pnl_x`/`calc_pnl_y` in the `TargetOrders` account are left in a state that reproduces the mismatch on every subsequent call (the state is only mutated when the function succeeds — see the success branch's fee/PnL bookkeeping [10](#0-9) ), every future `Deposit` and `Withdraw` against that pool will re-enter `calc_take_pnl` with the same stale `target.calc_pnl_x/y` and panic again, since nothing in the failing paths ever advances or repairs `calc_pnl_x`/`calc_pnl_y`.

### Impact Explanation
A panic inside a Solana program instruction aborts only the single transaction, but because the root cause is *persistent on-chain state* (`TargetOrders.calc_pnl_x`/`calc_pnl_y`), the condition is deterministic and repeatable: once triggered, every subsequent `Deposit` or `Withdraw` transaction against the affected pool will hit the same panic and revert. Because `process_withdraw` is the only path by which LPs can redeem their pool tokens for the underlying coin/pc, a pool stuck in this state permanently freezes LP funds — no LP can withdraw liquidity and no depositor can add liquidity, matching the "repeatable crash / hang causing DOS" bug class from the reference CVE, mapped onto this program's fund-availability guarantees.

### Likelihood Explanation
Reaching this code path only requires submitting ordinary, permission-less `Deposit` or `Withdraw` instructions with attacker-chosen amounts; no elevated signer, admin key, or off-chain component is needed. However, actually engineering the exact sequence of deposits/withdraws/swaps needed to force the native-vs-normalized rounding mismatch to flip `x2 > x1` (or `y2 > y1`) requires precise control over vault balances at the wei/lamport level and is dependent on token decimals and `sys_decimal_value`, which makes exploitation non-trivial but not implausible for a determined, low-privileged attacker — consistent with the "AC:H" (high attack complexity) rating of the reference CVE.

### Recommendation
Replace the `.unwrap()` calls on `x1.checked_sub(x2)` / `y1.checked_sub(y2)` (and the other bare `.unwrap()`s in `calc_take_pnl`) with `checked_sub(...).ok_or(AmmError::CalcPnlError)?` (or equivalent), returning a program error instead of panicking. Additionally, consider using `saturating_sub` or clamping `x2`/`y2` to `x1`/`y1` when the normalized invariant slightly overshoots due to rounding, so transient rounding noise does not brick pool operations; and ensure the pre-check comparison and the `x2`/`y2` derivation operate over the same numeric representation (either both native or both normalized) to eliminate the inconsistency at its source.

### Proof of Concept
1. Create a pool via `Initialize2` with token decimals that do not evenly divide `sys_decimal_value` (e.g., a coin with 9 decimals against `sys_decimal_value = 10^6`), so `normalize_decimal_v2`/`restore_decimal` round-trips lose precision [11](#0-10) .
2. Perform a sequence of small `Deposit`/`Withdraw`/`SwapBaseIn` calls with amounts chosen to shift `amm_pc_vault.amount`/`amm_coin_vault.amount` by values that survive the native-unit gate check but produce, once normalized, an `x2` (or `y2`) that exceeds `x1` (or `y1`) after `integer_sqrt()` rounding.
3. Submit the triggering `Deposit` or `Withdraw` instruction; `calc_take_pnl`'s `x1.checked_sub(x2).unwrap()` (or `y1.checked_sub(y2).unwrap()`) panics, aborting the transaction.
4. Because `TargetOrders.calc_pnl_x`/`calc_pnl_y` remain unchanged (the failing call never reaches the state-mutating success branch), every subsequent `Deposit`/`Withdraw` against the same pool reproduces the identical panic, permanently blocking withdrawals for all LPs.

### Citations

**File:** program/src/processor.rs (L167-214)
```rust
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
