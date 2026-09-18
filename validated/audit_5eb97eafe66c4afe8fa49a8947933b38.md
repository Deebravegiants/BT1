### Title
Unchecked division by pool reserves in `calc_x_power`/`calc_take_pnl` can panic (transaction-abort DoS) and, on a fully-drained pool, permanently freeze deposits/swaps - (File: `program/src/math.rs`, `program/src/processor.rs`)

### Summary
`Calculator::calc_x_power` performs `checked_div(current_y).unwrap()` and `calc_take_pnl` performs `x2.checked_mul(y1).unwrap().checked_div(x1).unwrap()` with no guard against the divisor being zero. `x1`/`y1` are the normalized "total pc/coin without take-pnl" pool balances that are recomputed and fed into this code on every `Deposit`, `Withdraw`, and `SwapBaseIn`/`SwapBaseOut` instruction path. This mirrors the CVE-2020-27760 bug class: a value derived from mutable, attacker-influenceable state (pool reserves) is used as a division denominator without a `PerceptibleReciprocal`-style zero-guard, so when that value reaches zero the `unwrap()` on `None` panics.

### Finding Description
`calc_x_power` divides by `current_y` (the normalized coin reserve) unconditionally: [1](#0-0) 

`calc_take_pnl` then divides by `x1` (the normalized pc reserve) when computing `y2`, and this whole routine is invoked from `Deposit`, `Withdraw`, and swap-adjacent flows with `x1`/`y1` derived from the live vault balances minus `need_take_pnl_*`: [2](#0-1) [3](#0-2) [4](#0-3) 

The swap-only `calc_take_pnl` guard `if amm.status != AmmStatus::WithdrawOnly` only skips the call during withdrawal when the pool is in `WithdrawOnly` status; deposit and normal-status withdrawal/swap paths always execute `calc_take_pnl`, meaning `x1`/`y1` == 0 is reachable whenever a pool's `total_pc_without_take_pnl` or `total_coin_without_take_pnl` reaches exactly zero (e.g., after a full/near-full drain via legitimate repeated `Withdraw`/`SwapBaseIn`/`SwapBaseOut` calls, or via `need_take_pnl_pc`/`need_take_pnl_coin` growing to equal the vault balance through repeated pnl accrual).

Because `x1`/`y1` come from live, non-attacker-signed but state-mutated pool reserves reachable through unprivileged instructions (`Deposit`, `Withdraw`, both swap variants), an unprivileged actor who drives one side of the pool reserve to zero (e.g., by being the final withdrawer, or by combining swaps that push `total_coin_without_take_pnl`/`total_pc_without_take_pnl` toward zero through rounding-favorable sequences) causes any subsequent call into `calc_take_pnl` to panic on `checked_div(0).unwrap()`.

### Impact Explanation
A panic inside `calc_take_pnl` aborts the calling transaction. Because `Deposit` (re-adding liquidity to the same `AmmInfo`/`TargetOrders` account) unconditionally calls `calc_take_pnl`, once a pool's `x1` or `y1` normalized reserve is driven to zero, every future `Deposit` transaction against that pool will panic and revert, permanently preventing anyone from re-adding liquidity to that specific pool — a form of permanent denial-of-service / freezing of the pool for LPs, satisfying the "permanent freezing of user/LP funds" bar. It does not itself cause fund theft, but it can strand any remaining dust in vaults from being pooled/withdrawn cleanly and blocks the pool's core `Deposit` code path indefinitely.

### Likelihood Explanation
Reaching an exact-zero `total_pc_without_take_pnl` or `total_coin_without_take_pnl` requires precise reserve conditions (a fully-drained side of the pool), which is a narrower trigger than the general swap/deposit flows and is partially mitigated by strict inequality checks (`>=`) in the swap output paths that prevent a single swap from zeroing out a reserve outright. However, `need_take_pnl_pc`/`need_take_pnl_coin` accrual combined with withdrawals is a state an unprivileged pool creator/LP could engineer over multiple self-controlled transactions on a pool they created, without needing any privileged signer.

### Recommendation
Add explicit zero-checks (or `PerceptibleReciprocal`-equivalent guards) before every `checked_div` in `calc_x_power`, `calc_take_pnl`, and related `Calculator` helpers, returning a defined `AmmError` (e.g., `AmmError::CalcPnlError` or a new `DivideByZero` variant) instead of relying on `unwrap()` panics whenever a reserve-derived divisor could be zero.

### Proof of Concept
Not independently executable from static review alone — reaching the zero-divisor state requires driving `total_coin_without_take_pnl` or `total_pc_without_take_pnl` to exactly zero through a sequence of legitimate `Withdraw`/`Swap` calls on a pool, which I could not fully trace end-to-end (exact arithmetic bounds enforced by the `>=` checks in `process_swap_base_in`/`process_swap_base_out` at [5](#0-4)  would need to be verified against withdrawal rounding behavior in `exchange_pool_to_token`) — this is flagged as an area of uncertainty rather than a confirmed exploit chain.

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

**File:** program/src/processor.rs (L159-209)
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
```

**File:** program/src/processor.rs (L1147-1173)
```rust
        // calc the remaining total_pc & total_coin
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

**File:** program/src/processor.rs (L2000-2004)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap_amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```
