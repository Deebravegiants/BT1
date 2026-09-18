### Title
Reachable panic (unwrap-on-None) in `Processor::calc_take_pnl` triggered from unprivileged `Deposit`/`Withdraw` due to decimal-normalization rounding mismatch - (File: `program/src/processor.rs`)

### Summary
The Envoy CVE (CVE-2022-29228) is a "reachable assertion" bug class: code invokes an operation whose safety invariant can be violated by attacker-influenced state, hitting an `ASSERT()`/panic that a privileged code path never checked for. Raydium's `calc_take_pnl` function contains an analogous reachable-panic pattern: it performs a boundary check in one numeric domain (raw token amounts) and then performs `checked_sub(...).unwrap()` on a *different, independently rounded* numeric domain (decimal-normalized `U256`/`U128` values), so integer truncation in the two paths can diverge at the boundary, causing the `unwrap()` to panic on a `None`. This function is invoked from `process_deposit` and `process_withdraw`, both callable by any liquidity provider with attacker-chosen `accounts`/instruction data.

### Finding Description
`Processor::calc_take_pnl` first checks, in raw (native) units: [1](#0-0) 
guarding entry into the pnl-taking branch. It then recomputes the same relationship in `sys_decimal_value`-normalized units via `Calculator::calc_x_power` and `integer_sqrt()`, and immediately subtracts without any fallback: [2](#0-1) 

Algebraically, the raw-unit check (`total_pc * total_coin >= restore_decimal(calc_pnl_x)*restore_decimal(calc_pnl_y)`) and the normalized-unit computation (`x2 = sqrt(calc_pnl_x*calc_pnl_y*x1/y1)`, compared against `x1`) are mathematically equivalent only under *exact* (real-number) arithmetic. In practice both `normalize_decimal_v2` and `restore_decimal` truncate on integer division: [3](#0-2) 
and `calc_x_power`/`integer_sqrt` introduce additional truncation: [4](#0-3) 
Because `pc_decimals` and `coin_decimals` frequently differ (e.g. 6 vs 9), and each quantity passes through a different chain of truncating divisions, the outer "current_k >= last_k" gate can pass by a hair while the inner `x2`/`y2` (computed via a different rounding path) end up strictly greater than `x1`/`y1`. When that happens, `x1.checked_sub(x2).unwrap()` (or the analogous `y1.checked_sub(y2).unwrap()`) returns `None` and the `unwrap()` panics — a reachable assertion/panic directly analogous to Envoy's reachable `ASSERT()`.

### Impact Explanation
`calc_take_pnl` is invoked from `process_deposit` and `process_withdraw`: [5](#0-4) [6](#0-5) 
Both are unprivileged, attacker-reachable instructions. An attacker can use ordinary swap instructions (`SwapBaseIn`/`SwapBaseOut`) to push the pool's `total_pc_without_take_pnl`/`total_coin_without_take_pnl` ratio arbitrarily close to the boundary where the raw-unit gate barely passes while the normalized recomputation rounds the other way. Once that state is reached, every subsequent `Deposit` or `Withdraw` call against the pool hits the panic and aborts, so legitimate LPs cannot deposit or withdraw — a denial-of-service that freezes LP funds in the pool for as long as the attacker can keep nudging the ratio back into the triggering window (a single small swap is enough to re-arm it after any state-shifting activity), satisfying the "permanent/attacker-sustained freezing of LP funds" impact bar.

### Likelihood Explanation
Reaching the vulnerable state only requires ordinary swaps (fully permissionless) to move `total_pc_without_take_pnl`/`total_coin_without_take_pnl` to a specific ratio near the boundary condition, then submitting a `Deposit` or `Withdraw` transaction. No privileged signer, no validator collusion, and no off-chain component is required — everything is driven by a single submitted transaction's attacker-chosen `amount_in`/`amount_out` and account set. The main uncertainty is the precision of the exact boundary (which depends on the pool's decimals and current reserves), which an attacker can search for off-chain by simulating `calc_take_pnl`'s arithmetic before submitting the triggering swap+deposit/withdraw sequence.

### Recommendation
Replace the unconditional `.unwrap()` calls on `x1.checked_sub(x2)` / `y1.checked_sub(y2)` in `calc_take_pnl` with saturating subtraction (clamping to zero) or an explicit re-check that returns `AmmError::CalcPnlError` when `x2 > x1` or `y2 > y1`, instead of relying on the outer raw-unit comparison as a proxy for the inner normalized-unit comparison. Ensure both checks are performed in the same numeric domain to eliminate rounding-induced divergence.

### Proof of Concept
1. Create a pool with `pc_decimals` ≠ `coin_decimals` (e.g. USDC/SOL, 6 vs 9), and perform an initial `Deposit`/`Initialize2` so `TargetOrders.calc_pnl_x`/`calc_pnl_y` are set.
2. Submit a sequence of `SwapBaseIn`/`SwapBaseOut` transactions with attacker-chosen `amount_in` to move `total_pc_without_take_pnl` and `total_coin_without_take_pnl` such that `total_pc * total_coin` is only marginally ≥ `restore_decimal(calc_pnl_x) * restore_decimal(calc_pnl_y)` (found via off-chain simulation of the exact integer arithmetic in `math.rs`/`processor.rs`).
3. Submit a `Deposit` or `Withdraw` instruction; `calc_take_pnl` recomputes `x2`/`y2` via the normalized/`sqrt` path, which — due to independent truncation — evaluates to a value fractionally larger than `x1`/`y1`, causing `checked_sub(...).unwrap()` to panic and the transaction to abort.
4. As long as the attacker keeps the ratio near this boundary (trivial with a follow-up small swap), all `Deposit`/`Withdraw` calls on the pool continue to panic, freezing LP funds. [7](#0-6)

### Citations

**File:** program/src/processor.rs (L167-281)
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

            let diff_pc_pnl_amount =
                Calculator::restore_decimal(diff_x, amm.pc_decimals, amm.sys_decimal_value);
            let diff_coin_pnl_amount =
                Calculator::restore_decimal(diff_y, amm.coin_decimals, amm.sys_decimal_value);
            let pc_pnl_amount = diff_pc_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
            let coin_pnl_amount = diff_coin_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
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
    }
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
