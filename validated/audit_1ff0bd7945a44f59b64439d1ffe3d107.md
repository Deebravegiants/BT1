### Title
Unconditional `checked_sub`/`.unwrap()` in PnL and take-pnl accounting causes permanent transaction failure (denial of service / freezing of pool funds) instead of a graceful zero result - (File: `program/src/math.rs`, `program/src/processor.rs`)

### Summary
`Calculator::calc_total_without_take_pnl_no_orderbook` subtracts the pool's outstanding, not-yet-withdrawn PnL (`amm.state_data.need_take_pnl_pc` / `need_take_pnl_coin`) from the live vault balances using `checked_sub(...).ok_or(AmmError::CheckedSubOverflow)?`. [1](#0-0) 
This function is invoked, unconditionally and on every call, by `process_deposit`, `process_withdraw`, `process_withdrawpnl`, `process_swap_base_in`, `process_swap_base_out`, `process_swap_base_in_v2`, and `process_swap_base_out_v2` — i.e. every user-facing instruction that touches the AMM pool. [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) 

If, for any reason, the real vault balance (`amm_pc_vault.amount` / `amm_coin_vault.amount`) ever becomes smaller than the recorded `need_take_pnl_*` counter, this subtraction underflows and every subsequent call to any of the above instructions returns `AmmError::CheckedSubOverflow` and reverts — exactly the "should return zero but instead the transaction crashes" bug class described in the external report for CoverFlashLoan.

### Finding Description
`need_take_pnl_pc`/`need_take_pnl_coin` are pool-owner-reserved PnL fee amounts that are accumulated inside vault balances by `calc_take_pnl`, which grows them via `checked_add` based on a sqrt-based invariant calculation performed in a different fixed-point decimal domain (`sys_decimal_value`) than the raw token amounts, using `normalize_decimal_v2`/`restore_decimal`, both of which truncate (floor) on every conversion. [8](#0-7) [9](#0-8) 

Because `calc_take_pnl` is re-derived from scratch on every deposit/withdraw/swap/withdrawpnl call from the *current* vault balances and `target_orders.calc_pnl_x/y` (rather than being strictly monotonic bookkeeping tied 1:1 to real transfers), repeated truncation/rounding in the decimal round-trips, combined with `need_take_pnl_pc`/`need_take_pnl_coin` being persisted state that is only ever incremented (via `checked_add`, never reduced except on `process_withdrawpnl`) can drift out of sync with the true vault balances over many operations. Once `pc_amount < amm.state_data.need_take_pnl_pc` (or the coin equivalent) for any reason — rounding drift, a withdrawal that removes more of the real balance than the "without-pnl" share it was entitled to, or any other benign edge condition — the `checked_sub` in `calc_total_without_take_pnl_no_orderbook` fails and the instruction reverts with `AmmError::CheckedSubOverflow` instead of clamping to zero.

Because this helper sits at the very front of every pool-mutating instruction (`SwapBaseIn`, `SwapBaseOut`, `SwapBaseInV2`, `SwapBaseOutV2`, `Deposit`, `Withdraw`, `WithdrawPnl`), once the underflow condition is hit, it does not merely fail one transaction — it permanently bricks the pool: no swapper can swap, no LP can deposit or withdraw, and the AMM owner cannot even reclaim the stuck PnL because `process_withdrawpnl` calls the exact same helper before it can process the fix. [10](#0-9) 

This mirrors the CoverFlashLoan pattern precisely: a subtraction that is expected to legitimately reach (or cross) zero is implemented with a hard-reverting `checked_sub` instead of a saturating/clamped computation, converting a benign boundary case into an unconditional DoS.

### Impact Explanation
If triggered, this freezes all LP and swapper funds already deposited in the pool's vaults — swaps, deposits, and withdrawals (both regular LP withdrawal and PnL withdrawal) all become permanently unusable since they all depend on `calc_total_without_take_pnl_no_orderbook` succeeding. This is a fund-freezing denial-of-service impacting every user of the affected pool, not just the transaction sender, which satisfies the "permanent freezing of user or LP funds" impact bar.

### Likelihood Explanation
The trigger does not require a privileged signer, leaked key, or off-chain component — it can occur purely from the interaction of ordinary swap/deposit/withdraw instructions accumulating rounding drift between the truncating decimal-normalization math (`normalize_decimal_v2`/`restore_decimal`) and the persisted `need_take_pnl_*` counters across many transactions submitted by ordinary, unprivileged users. Because `calc_take_pnl` only ever increases `need_take_pnl_pc`/`need_take_pnl_coin` via `checked_add` and is never reconciled downward against real vault flows except in the lockstep-checked `process_withdrawpnl` path, the invariant `vault.amount >= need_take_pnl_*` is not provably maintained under composition of the different math paths (swap fee accrual vs. LP withdrawal proportional accounting vs. decimal truncation), making this a realistic occurrence over the life of an active pool rather than a purely theoretical one.

### Recommendation
Change `calc_total_without_take_pnl_no_orderbook` in `program/src/math.rs` to saturate to zero instead of reverting when `pc_amount`/`coin_amount` is smaller than the corresponding `need_take_pnl_*` value, e.g.:
```rust
let total_pc_without_take_pnl = pc_amount.saturating_sub(amm.state_data.need_take_pnl_pc);
let total_coin_without_take_pnl = coin_amount.saturating_sub(amm.state_data.need_take_pnl_coin);
```
This matches the recommended fix pattern from the external report (explicit `if` check returning zero rather than reverting on an inherently reachable "PnL exceeds available balance" boundary condition), while keeping the invariant checks in `process_withdrawpnl` (lines 1505-1507) intact as the authoritative safety net for actual fund transfers.

### Proof of Concept
Concrete on-chain reproduction requires driving `need_take_pnl_pc`/`need_take_pnl_coin` above the real vault balance through a specific sequence of swaps/deposits/withdrawals that exploit the decimal-truncation drift in `normalize_decimal_v2`/`restore_decimal`/`calc_take_pnl`; a precise minimal sequence of instructions and amounts to deterministically force the underflow was not verified within the scope of this analysis (this would require simulation/fuzzing against the exact fee/decimal parameters of a deployed pool). The code-level root cause — an unconditional `checked_sub` reachable from every pool instruction with no recovery path — is confirmed directly in `program/src/math.rs:238-250` and its seven call sites in `program/src/processor.rs`.

### Citations

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

**File:** program/src/processor.rs (L167-266)
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
```

**File:** program/src/processor.rs (L1148-1153)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1459-1464)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
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

**File:** program/src/processor.rs (L2342-2347)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L2533-2538)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```
