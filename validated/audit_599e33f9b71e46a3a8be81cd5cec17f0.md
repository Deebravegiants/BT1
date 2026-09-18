### Title
Division-by-zero panic in `Processor::calc_take_pnl` can permanently freeze pool operations - ([File: program/src/processor.rs])

### Summary
`Processor::calc_take_pnl`, invoked from the `Deposit`, `Withdraw`, and `WithdrawPnl` instruction handlers, performs an unchecked `checked_div(x1).unwrap()` where `x1` is a value derived directly from the live token-vault balance minus the pool's accumulated `need_take_pnl_pc`. If an attacker can drive `total_pc_without_take_pnl` (and thus `x1`) to exactly zero through ordinary swap activity, every subsequent call into `calc_take_pnl` will panic and abort, permanently bricking `Deposit`, `Withdraw`, and `WithdrawPnl` for that pool — an on-chain analog of the Bento4 `GetSample` NULL-pointer crash triggered by unchecked/attacker-influenced input.

### Finding Description
`calc_take_pnl` computes the "current price" ratio as `x2.checked_mul(y1).unwrap().checked_div(x1).unwrap()` (`y2`), where: [1](#0-0) 

`x1`/`y1` are computed upstream by `Calculator::calc_total_without_take_pnl_no_orderbook`, which subtracts the pool's stored `need_take_pnl_pc`/`need_take_pnl_coin` from the live vault balances with no protection against the result reaching zero: [2](#0-1) 

`calc_take_pnl` is reached from every liquidity-affecting instruction that an unprivileged user can call directly — `process_deposit` at [3](#0-2) ,
`process_withdraw` at [4](#0-3) ,
and `process_withdrawpnl` (callable by the configured `pnl_owner`) at [5](#0-4) .

`need_take_pnl_pc`/`need_take_pnl_coin` are incremented inside `calc_take_pnl` itself whenever the pool's current invariant `k` exceeds the last recorded `calc_pnl_x * calc_pnl_y`, which is a normal, attacker-triggerable consequence of repeated swaps in one direction: [6](#0-5) 

Because `need_take_pnl_pc`/`need_take_pnl_coin` are only reset when `WithdrawPnl` is successfully executed by the privileged `pnl_owner`, an unprivileged swapper can, through a sequence of ordinary `SwapBaseIn`/`SwapBaseOut` calls with attacker-chosen amounts, drive `pc_amount - need_take_pnl_pc` (or the coin equivalent) to exactly zero. Unlike the swap handlers themselves — which explicitly guard against the output amount reaching or exceeding `total_pc_without_take_pnl` via `if swap_amount_out >= total_pc_without_take_pnl { return Err(...) }` — `calc_take_pnl`'s internal division has no equivalent zero-check before the `unwrap()`.

Once `x1` (or `y1`) is zero, any future call to `Deposit`, `Withdraw`, or `WithdrawPnl` recomputes the same zero value from the persisted `need_take_pnl_pc`/vault balance and panics again, since a failed transaction does not roll back the on-chain state that produced the zero denominator (the vault balances and `need_take_pnl_pc` are unaffected by the aborted transaction). This differs qualitatively from a simple transient revert: it is a stable, reproducible state that makes the affected instructions permanently unusable for that pool.

### Impact Explanation
A successful trigger permanently freezes `Deposit`, `Withdraw`, and `WithdrawPnl` for the affected AMM pool (Solana program panics abort but do not roll back already-committed prior state that caused the divide-by-zero condition), preventing LPs from withdrawing their liquidity and preventing PnL owners from withdrawing accrued fees. This matches the "permanent freezing of user or LP funds" impact bar.

### Likelihood Explanation
Triggering requires an attacker to compute (from fully public on-chain state: vault balances, `need_take_pnl_pc/coin`, fee parameters) a precise sequence/size of swaps that drives `pc_amount - need_take_pnl_pc` (or the coin equivalent) to exactly zero. All required accounts (vaults, `AmmInfo`, `TargetOrders`) and instruction data are attacker-controllable inputs to `SwapBaseIn`/`SwapBaseOut`, both of which are unprivileged, single-transaction entry points, making this reachable without any special privileges, though it does require exact arithmetic targeting.

### Recommendation
Replace the unchecked `.unwrap()` divisions in `calc_take_pnl` (and the underlying `checked_div` calls that depend on `x1`/`y1`) with `checked_div(...).ok_or(AmmError::CheckedDivOverflow)?` style handling, and treat a zero denominator as "no pnl to take" (skip the pnl-taking branch) rather than panicking.

### Proof of Concept
1. An attacker repeatedly calls `SwapBaseIn`/`SwapBaseOut` in a consistent direction on a pool, each time causing `calc_take_pnl` to add to `amm.state_data.need_take_pnl_pc` (as shown at `program/src/processor.rs:244-262`), while the vault's raw `pc_amount` decreases via swap outflows.
2. Because the attacker can observe the exact current values of `pc_amount`, `need_take_pnl_pc`, and fee parameters on-chain, they can compute a final swap whose resulting `total_pc_without_take_pnl = pc_amount - need_take_pnl_pc` equals exactly `0`.
3. Any subsequent call to `Deposit`, `Withdraw`, or `WithdrawPnl` recomputes `x1 = normalize_decimal_v2(0, ...) = 0` and then panics at `checked_div(x1).unwrap()` inside `calc_take_pnl` (`program/src/processor.rs:208`), aborting the transaction.
4. Since the on-chain state (`need_take_pnl_pc`, vault balance) that produces the zero denominator persists regardless of the abort, every future attempt to deposit, withdraw, or withdraw pnl on this pool fails identically, permanently freezing pool funds.

### Citations

**File:** program/src/processor.rs (L199-209)
```rust
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

**File:** program/src/processor.rs (L1145-1153)
```rust
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
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
