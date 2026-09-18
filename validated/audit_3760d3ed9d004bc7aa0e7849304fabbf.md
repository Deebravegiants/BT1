### Title
Reachable panic (division-by-zero unwrap) in `calc_take_pnl`/`calc_x_power` permanently bricks Deposit, Withdraw and WithdrawPnl once a pool side is fully claimed by pending PNL - (File: `program/src/processor.rs`, `program/src/math.rs`)

### Summary
This is the same bug class as the Nimiq advisory (CWE-787/"Reachable Assertion"): an unprivileged, attacker-reachable code path performs an unchecked arithmetic operation (`checked_div(...).unwrap()`) on a value that can legitimately become zero, causing a hard panic instead of a graceful error. In Raydium AMM, this path is `Calculator::calc_x_power`, invoked from `Processor::calc_take_pnl`, which itself is called from `process_deposit`, `process_withdraw`, and `process_withdrawpnl` — the exact instruction set an unprivileged swapper/LP is expected to reach.

### Finding Description
`Processor::calc_take_pnl` computes the "current" normalized reserves `x1`/`y1` from `total_pc_without_take_pnl` and `total_coin_without_take_pnl` (i.e., vault balances minus `amm.state_data.need_take_pnl_pc/coin`): [1](#0-0) 

It then calls `Calculator::calc_x_power(target.calc_pnl_x, target.calc_pnl_y, x1, y1)`, which divides by `current_y` (i.e., `y1`) with an unchecked `.unwrap()`: [2](#0-1) 

`calc_take_pnl` is invoked identically from three unprivileged/pnl-owner instructions, always passing the freshly computed `x1`/`y1` before any bounds validation of those specific values: [3](#0-2) [4](#0-3) 

`total_pc_without_take_pnl`/`total_coin_without_take_pnl` are derived via a `checked_sub` of `need_take_pnl_pc`/`need_take_pnl_coin` from the vault balances, which can legitimately reach exactly `0` (not an error, since `checked_sub` succeeds at the boundary): [1](#0-0) 

If either `total_pc_without_take_pnl` or `total_coin_without_take_pnl` is `0`, then `x1` or `y1` (its normalized form) is `0`: [5](#0-4) 

Passing `y1 = 0` as `current_y` into `calc_x_power` causes `checked_div(current_y)` to return `None`, and the subsequent `.unwrap()` panics. Since `calc_take_pnl` is called before `need_take_pnl_pc/coin` are reset to zero (the reset happens only after successful pnl transfer), `process_withdrawpnl` — the only instruction that could relieve the stuck state — hits the same panic, permanently bricking all three code paths for the pool.

### Impact Explanation
Once `need_take_pnl_pc` or `need_take_pnl_coin` reaches exactly the corresponding vault balance (achievable by an attacker driving pool price divergence through repeated swaps, since `need_take_pnl_*` accrues based on the price-vs-target-orders invariant computed in this same function), any subsequent call to `process_deposit`, `process_withdraw`, or `process_withdrawpnl` panics inside `calc_x_power`. Because Solana aborts only the failing transaction (not the validator process), the direct effect is not a node crash as in the Nimiq case, but a **permanent denial of service on Deposit/Withdraw/WithdrawPnl for that pool** — LPs can no longer withdraw their funds and the pnl owner cannot clear the stuck PNL balance, since every one of the only three paths that touch `need_take_pnl_*` panics. This constitutes permanent freezing of LP funds in the affected pool.

### Likelihood Explanation
Reaching this state requires precisely driving `total_pc_without_take_pnl` or `total_coin_without_take_pnl` to exactly `0` via `need_take_pnl_pc`/`need_take_pnl_coin` accrual, which happens through the swap-driven PNL accounting inside `calc_take_pnl`'s own `if` branch: [6](#0-5) 
This requires careful (but attacker-fully-controlled) sequencing of swap amounts and possibly deposit/withdraw calls to land exactly on the boundary, given all inputs (`amount_in`, `amount_out`, deposit/withdraw amounts) are attacker-chosen in a single or few transactions. This is a non-trivial but plausible griefing/DoS setup exploitable by any unprivileged actor without special signer privileges.

### Recommendation
Replace the unchecked `.unwrap()` calls in `Calculator::calc_x_power` (and the related `checked_sub`/`checked_div`/`checked_mul` chains in `calc_take_pnl`) with proper error propagation (`ok_or(AmmError::...)?`), and add an explicit early-return guard in `calc_take_pnl` when `x1 == 0 || y1 == 0`, returning a domain error instead of proceeding into division. This mirrors the referenced Nimiq patch pattern of adding a guard before the operation that can panic on a boundary value.

### Proof of Concept
1. Attacker (or coordinated actors) performs swaps against the pool to accumulate `need_take_pnl_coin` (or `_pc`) via the PNL-accrual branch in `calc_take_pnl` until it equals `amm_coin_vault.amount` (or `amm_pc_vault.amount`) exactly — `calc_total_without_take_pnl_no_orderbook`'s `checked_sub` succeeds and yields `0`.
2. Any subsequent call to `process_deposit` or `process_withdraw` computes `y1 = normalize_decimal_v2(0, ...) = 0` and passes it into `calc_take_pnl` → `calc_x_power`, where `checked_div(current_y).unwrap()` panics, aborting the transaction.
3. `process_withdrawpnl`, the only instruction that could reduce `need_take_pnl_coin`/`pc` back below the vault balance, computes the same `x1`/`y1` from the still-stuck state before any transfer, and also calls `calc_take_pnl` first — so it panics identically, leaving the pool permanently unable to process Deposit, Withdraw, or WithdrawPnl.

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

**File:** program/src/processor.rs (L190-266)
```rust
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

**File:** program/src/processor.rs (L1458-1502)
```rust
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        msg!(arrform!(
            LOG_SIZE,
            "withdrawpnl need_take_coin:{}, need_take_pc:{}",
            identity(amm.state_data.need_take_pnl_coin),
            identity(amm.state_data.need_take_pnl_pc)
        )
        .as_str());

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
        msg!(arrform!(
            LOG_SIZE,
            "withdrawpnl total_pc:{}, total_coin:{}, x:{}, y:{}",
            total_pc_without_take_pnl,
            total_coin_without_take_pnl,
            x1,
            y1
        )
        .as_str());

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
