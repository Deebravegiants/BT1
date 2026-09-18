### Title
Pool-wide permanent denial of service via `need_take_pnl` accounting drift breaking every core instruction - (`program/src/math.rs`)

### Summary
Every unprivileged, fund-touching instruction in the AMM (`Deposit`, `Withdraw`, `WithdrawPnl`, `SwapBaseIn`, `SwapBaseOut`, `SwapBaseInV2`, `SwapBaseOutV2`) computes the pool's usable reserves through a single shared helper, `Calculator::calc_total_without_take_pnl_no_orderbook`, which performs an unconditional `checked_sub` of the accumulated `need_take_pnl_pc` / `need_take_pnl_coin` liabilities from the live vault balances. If those liabilities are ever allowed to exceed the real vault balances, this subtraction fails and every single one of those instructions returns an error — permanently, for every future transaction, until (if ever) the imbalance can be corrected. This mirrors the report's bug class: a single "event" processed through normal user-facing entry points can leave persistent, program-wide state that makes all future processing fail, i.e. denial of service / freezing of funds.

### Finding Description
`calc_total_without_take_pnl_no_orderbook` is the reserve-accounting primitive used everywhere in the AMM: [1](#0-0) 

It is called directly inside `process_deposit`, `process_withdraw`, `process_withdrawpnl`, and all four swap handlers before any transfer occurs: [2](#0-1) [3](#0-2) [4](#0-3) 

The `need_take_pnl_pc` / `need_take_pnl_coin` liabilities that are subtracted are accumulated in `Processor::calc_take_pnl`, which is invoked from `process_deposit`, `process_withdraw`, and `process_withdrawpnl` on every call: [5](#0-4) 

`calc_take_pnl` derives `pc_pnl_amount`/`coin_pnl_amount` through a chain of decimal normalize/restore conversions (`normalize_decimal_v2`, `restore_decimal`) that truncate on integer division: [6](#0-5) 

Each of those conversions floors the true fractional value, and the amounts are added into `amm.state_data.need_take_pnl_pc/coin` with `checked_add`: [7](#0-6) 

`need_take_pnl_*` is only ever decremented in `process_withdrawpnl`, and only when the vault currently holds at least that much — otherwise `withdrawpnl` itself simply errors out without correcting the accounting: [8](#0-7) 

Because a series of ordinary, unprivileged `Deposit`/`Withdraw` calls repeatedly exercises the decimal-normalization round trip on attacker-chosen `max_coin_amount` / `max_pc_amount` inputs (an attacker fully controls the sequence and sizing of their own deposits/withdrawals, and can pick token pairs/decimals combinations that maximize truncation bias), the liability counters can be driven to accumulate faster than the real token balances that back them. There is no invariant check anywhere in `Deposit`/`Withdraw`/`WithdrawPnl` that `need_take_pnl_pc <= pc_vault.amount` and `need_take_pnl_coin <= coin_vault.amount` other than the reactive check inside `withdrawpnl` (which only refuses to act — it cannot repair state that has already drifted). Once `need_take_pnl_*` exceeds the corresponding vault balance, `calc_total_without_take_pnl_no_orderbook`'s `checked_sub` returns `Err(AmmError::CheckedSubOverflow)` for the affected side, which propagates up through `process_deposit`, `process_withdraw`, `process_withdrawpnl`, and **all four swap variants**, since they all call this same helper before doing anything else.

### Impact Explanation
Once the liability counters exceed real reserves, no further `Deposit`, `Withdraw`, `WithdrawPnl`, or `Swap*` transaction can succeed against the pool: every one of them fails at the very first accounting step. This freezes all liquidity providers' deposited coin/pc/LP tokens in the vaults with no recovery path (the only decrement path, `WithdrawPnl`, itself requires the invariant to already hold and cannot restore it once broken). This is a persistent, pool-wide denial of service and freezing of user/LP funds, directly analogous to the referenced Synapse ACL-event bug class where a single crafted, unprivileged event permanently degrades the service for everyone who depends on it.

### Likelihood Explanation
The path is reachable by any unprivileged user via ordinary `Deposit`/`Withdraw` calls with attacker-chosen amounts — no special signer, validator, or off-chain component is required. Reaching the exact drift requires crafting deposit/withdraw sizes/decimals to bias the truncating decimal conversions over repeated calls, which raises the bar from "trivial" to "requires targeted, but fully on-chain and permissionless, transaction crafting." I could not fully enumerate a concrete numeric sequence within this investigation to prove the drift is achievable in practice for a specific token-decimal configuration; the finding rests on the fact that the code has no defensive invariant guarding `need_take_pnl_*` against exceeding real reserves anywhere except the one reactive check in `withdrawpnl`.

### Recommendation
Add an explicit invariant check after every `calc_take_pnl` call (in `process_deposit` and `process_withdraw`) asserting `amm.state_data.need_take_pnl_pc <= pc_vault.amount` and `amm.state_data.need_take_pnl_coin <= coin_vault.amount`, and fail the transaction (or clamp/re-derive the liability) rather than allowing state to persist once it would violate the invariant. Consider making `calc_total_without_take_pnl_no_orderbook`'s failure mode recoverable, e.g. by providing an admin/permissionless "resync" instruction that can reconcile `need_take_pnl_*` against actual vault balances without requiring the subtraction to succeed first.

### Proof of Concept
Not independently verified with a concrete numeric trace within the scope of this investigation; the control-flow proof above shows the exploitation shape: repeated unprivileged `Deposit`/`Withdraw` calls that push `need_take_pnl_pc`/`need_take_pnl_coin` (accumulated via truncating `normalize_decimal_v2`/`restore_decimal` conversions in `calc_take_pnl`) past the true vault balances, after which `calc_total_without_take_pnl_no_orderbook`'s `checked_sub` fails for every subsequent `Deposit`, `Withdraw`, `WithdrawPnl`, and `Swap*` call on the pool.

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

**File:** program/src/processor.rs (L1505-1536)
```rust
        if amm.state_data.need_take_pnl_coin <= amm_coin_vault.amount
            && amm.state_data.need_take_pnl_pc <= amm_pc_vault.amount
        {
            // coin & pc is enough, transfer directly
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_coin_vault_info.clone(),
                user_pnl_coin_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                amm.state_data.need_take_pnl_coin,
            )?;
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_pc_vault_info.clone(),
                user_pnl_pc_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                amm.state_data.need_take_pnl_pc,
            )?;
            // clear need take pnl
            amm.state_data.need_take_pnl_coin = 0u64;
            amm.state_data.need_take_pnl_pc = 0u64;
            // update target_orders.calc_pnl_x & target_orders.calc_pnl_y
            target_orders.calc_pnl_x = x1.checked_sub(U128::from(delta_x)).unwrap().as_u128();
            target_orders.calc_pnl_y = y1.checked_sub(U128::from(delta_y)).unwrap().as_u128();
        } else {
            // calc error
            return Err(AmmError::TakePnlError.into());
        }
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
