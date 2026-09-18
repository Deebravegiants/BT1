### Title
Instantaneous pool reserves used as "current price" in `calc_take_pnl` can be manipulated via an atomic swap to skew LP mint/withdraw amounts - ([File: program/src/processor.rs])

### Summary
The MONT report shows that reading a manipulable, single-block "spot price" for a critical payout calculation lets an attacker sandwich the read to steal value. Raydium's `Deposit`, `Withdraw` and `WithdrawPnl` handlers exhibit the same root-cause pattern: they read the *current, unprotected* pool reserves (`amm_pc_vault.amount` / `amm_coin_vault.amount`) as `x1`/`y1` and feed them straight into `Processor::calc_take_pnl`, which uses that instantaneous ratio as "current price" to decide how much of the pool's value is peeled off into `need_take_pnl_pc/coin` before the LP-mint/burn math runs, all in the same instruction/transaction.

### Finding Description
`calc_take_pnl` is documented as computing `current_price = current_x / current_y` from the live vault balances and using it to find a point `(x2, y2)` on the pool's price ray that preserves the last checkpointed invariant (`calc_pnl_x * calc_pnl_y`): [1](#0-0) 

The "current price" inputs (`x1`, `y1`) are derived directly from live vault token balances at call time, with no TWAP/oracle or time-weighting: [2](#0-1) 
The same pattern repeats in `process_withdraw` and `process_withdrawpnl`: [3](#0-2) [4](#0-3) 

Because Solana lets a single transaction bundle multiple instructions atomically, an unprivileged actor can call `SwapBaseIn`/`SwapBaseOut` (or `SwapBaseInV2`/`SwapBaseOutV2`) immediately before `Deposit` or `Withdraw` in the *same* transaction, shifting the vault balances (and thus `x1`/`y1`) before the pnl calculation runs. The swap simultaneously grows `k = total_pc * total_coin` slightly (via the trade fee), satisfying the `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_pnl_y` precondition that gates `calc_take_pnl`: [5](#0-4) 

`calc_take_pnl` then computes `diff_x = x1 - x2`, `diff_y = y1 - y2` along the manipulated price ray and subtracts a `pnl_numerator/denominator` fraction of that split from `total_pc_without_take_pnl`/`total_coin_without_take_pnl` before those totals are used for LP share math: [6](#0-5) 

Those *already-reduced* totals are then used to compute `mint_lp_amount` on `Deposit`: [7](#0-6) 
and to compute `coin_amount`/`pc_amount` on `Withdraw`: [8](#0-7) 

Because the split between `delta_x` (pc taken as pnl) and `delta_y` (coin taken as pnl) is determined by the manipulated instantaneous ratio, an attacker can choose a swap direction that disproportionately depletes one side of `total_*_without_take_pnl` right before depositing on the *opposite* base side (`deposit.base_side`), causing `mint_lp_amount` to be computed against an artificially shrunk denominator and over-minting LP tokens for the same deposited amount — diluting existing LP holders. The reverse manipulation before a `Withdraw` can be used to extract a disproportionate share of `total_coin_without_take_pnl`/`total_pc_without_take_pnl` relative to a withdrawer's true pool share. The attacker can then reverse the initial swap in the same transaction to restore price and avoid directional market risk, isolating the profit to the pnl-accounting skew.

### Impact Explanation
This allows any unprivileged user who can construct a single transaction combining a swap with a `Deposit` or `Withdraw` to mint an inflated LP position or withdraw a disproportionate share of pooled coin/pc, directly transferring value from existing liquidity providers to the attacker. This matches "insolvent pool accounting" / theft of LP funds, consistent with High severity in the source report, since the loss is borne by all other LPs in the pool and is not bounded by a slippage-style user-set minimum (the `other_amount_min`/`max_*_amount` checks in `Deposit` only protect the deposit ratio between coin and pc, not the "current price" used internally for the pnl/invariant adjustment).

### Likelihood Explanation
Likelihood is Medium: it requires precise construction of an atomic transaction (swap + deposit/withdraw, possibly plus a reversing swap) and requires the `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_pnl_y` gating condition to hold, which depends on the pool's current state relative to its last pnl checkpoint. It does not require any privileged role, leaked keys, or off-chain assumptions — any address can submit `SwapBaseIn`/`SwapBaseOut` and `Deposit`/`Withdraw` with attacker-chosen amounts in one transaction.

### Recommendation
Do not derive the pnl-checkpoint "current price" from the same-transaction, single-slot vault balances that a caller can manipulate immediately beforehand. Use a time-weighted or otherwise manipulation-resistant reference (e.g., a running/last-slot snapshot updated once per slot, or restrict `calc_take_pnl` invocation to occur only via `WithdrawPnl` under permissioned control, decoupled from user-triggered `Deposit`/`Withdraw` calls), and/or add a check that rejects `Deposit`/`Withdraw` if the pool composition changed by more than a bounded amount within the same transaction/slot.

### Proof of Concept
Conceptual (cannot be executed without transaction simulation/on-chain harness access):
1. Attacker submits a single transaction containing:
   a. `SwapBaseIn` swapping a large amount of coin→pc (or pc→coin), shifting `amm_coin_vault`/`amm_pc_vault` balances and slightly growing `k` via the swap fee.
   b. `Deposit` (or `Withdraw`) immediately following, in the same transaction, before any other actor's transaction can execute in between.
2. Inside `Deposit`, `calc_total_without_take_pnl_no_orderbook` reads the just-manipulated `amm_pc_vault.amount`/`amm_coin_vault.amount` [9](#0-8) , and `calc_take_pnl` computes a skewed `delta_x`/`delta_y` split based on that manipulated ratio [10](#0-9) .
3. `mint_lp_amount` is computed against the resulting artificially reduced `total_coin_without_take_pnl` (or `total_pc_without_take_pnl`) [7](#0-6) , minting more LP tokens than the attacker's deposit is actually worth relative to the pool's true state.
4. Attacker optionally reverses the initial swap in the same transaction to restore the pool price, then redeems the over-minted LP tokens via `Withdraw` for a net profit at other LPs' expense.

Note: I was unable to fully verify the exact numeric magnitude of exploitable profit (bounded by the pool's accumulated-but-uncollected fee revenue since the last pnl checkpoint) without running the on-chain math end-to-end; a background Devin session with a local validator/test harness would be needed to quantify concrete extractable amounts under realistic parameters.

### Citations

**File:** program/src/processor.rs (L159-174)
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
```

**File:** program/src/processor.rs (L188-192)
```rust
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L199-266)
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

**File:** program/src/processor.rs (L1243-1250)
```rust
            // coin_amount/ (total_coin_amount + coin_amount)  = output / (lp_mint.supply + output) =>  output = coin_amount / total_coin_amount * lp_mint.supply
            let invariant_coin = InvariantPool {
                token_input: deduct_coin_amount,
                token_total: total_coin_without_take_pnl,
            };
            mint_lp_amount = invariant_coin
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
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

**File:** program/src/processor.rs (L1751-1761)
```rust
        // coin_amount / total_coin_amount = amount / lp_mint.supply => coin_amount = total_coin_amount * amount / pool_mint.supply
        let invariant = InvariantPool {
            token_input: withdraw.amount,
            token_total: amm.lp_amount,
        };
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
```
