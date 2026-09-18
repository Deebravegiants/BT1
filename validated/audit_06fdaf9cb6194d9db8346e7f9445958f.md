### Title
Instantaneous vault-ratio "current price" used in PnL take without TWAP protection enables single-transaction price manipulation of LP mint/burn accounting - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` derives a "current price" purely from the instantaneous coin/pc vault balances (`x1`/`y1`, computed from `amm_pc_vault.amount` / `amm_coin_vault.amount` at call time) and uses it to decide how much of the pool is skimmed into the `need_take_pnl_pc`/`need_take_pnl_coin` buckets before the remaining `total_pc_without_take_pnl` / `total_coin_without_take_pnl` are used to price LP mint/redeem ratios in `Deposit`/`Withdraw`. This is the same bug class as the reported `slot0`-based spot price read: a manipulable, un-TWAP'd, single-block/single-transaction price feed is used for a critical accounting decision.

### Finding Description
`calc_take_pnl` documents its own algorithm as computing "current price = current_x / current_y" directly from live reserves and using it to rebase the pool's internal invariant: [1](#0-0) 

The `x1`/`y1` values fed into this function are the normalized current `amm_pc_vault.amount` and `amm_coin_vault.amount` read at the top of `process_deposit`/`process_withdraw`, with no time-weighting or manipulation resistance: [2](#0-1) 

Inside `calc_take_pnl`, this instantaneous ratio determines `x2`/`y2` (the invariant point after "taking pnl"), and the resulting `delta_x`/`delta_y` are converted into real token amounts and moved out of `total_pc_without_take_pnl`/`total_coin_without_take_pnl` into `need_take_pnl_pc`/`need_take_pnl_coin`: [3](#0-2) 

Because `total_pc_without_take_pnl`/`total_coin_without_take_pnl` (post-pnl-adjustment) are exactly what `Deposit`/`Withdraw` subsequently use to compute `deduct_pc_amount`, `deduct_coin_amount`, and `mint_lp_amount`: [4](#0-3) 

...an attacker can, within a single attacker-controlled transaction, first issue a `SwapBaseIn`/`SwapBaseOut` instruction against the pool (any of the four permissionless swap instructions) to skew the coin/pc vault ratio, then immediately chain a `Deposit` (or `Withdraw`) instruction. The skewed instantaneous ratio changes how much value `calc_take_pnl` reclassifies as "pnl" versus how it prices the attacker's own deposit/withdrawal against `total_*_without_take_pnl`, and the swap can be reversed later in the same or a following transaction, since the pool's own bonding-curve swap math offers no cost beyond the trade fee for round-tripping.

### Impact Explanation
Manipulating the instantaneous ratio used by `calc_take_pnl` lets an attacker bias the LP mint/redeem ratio computed in `Deposit`/`Withdraw`, i.e. change how many LP tokens are minted for a given deposit or how much of `total_pc_without_take_pnl`/`total_coin_without_take_pnl` is skimmed into `need_take_pnl_*` immediately before/after their own deposit or withdrawal. This can result in unbacked/under-collateralized LP minting relative to other LPs' shares, or a distorted pnl allocation that misstates the pool's real solvency, directly affecting other LPs' redeemable value — the same class of harm (incorrect valuation → mispriced mint/redeem → fund loss for other participants) described in the reported `slot0` spot-price manipulation issue.

### Likelihood Explanation
`Deposit` and `Withdraw` are both permissionless, unprivileged instructions reachable by any user with attacker-chosen accounts/amounts, and can be freely combined with the four permissionless swap instructions in the same transaction (Solana composability), so no privileged signer or off-chain component is required to set up the manipulation.

### Recommendation
Do not derive the pnl-take "current price" (and by extension the deposit/withdraw pricing ratio) solely from the instantaneous vault balances read in the same instruction. Use a time-weighted or otherwise manipulation-resistant measure of reserves (e.g., snapshotting reserves prior to the transaction, or rejecting pnl-take/deposit processing when reserves have moved beyond an acceptable bound within the same slot/transaction), and add slippage/ratio-deviation checks around `calc_take_pnl`'s effect on `total_pc_without_take_pnl`/`total_coin_without_take_pnl` before they are used for LP mint/burn math.

### Proof of Concept
1. Attacker submits a single transaction with instructions:
   a. `SwapBaseIn` (or `SwapBaseOut`) with a large `amount_in` to skew `amm_coin_vault`/`amm_pc_vault` balances (`process_swap_base_in`, `program/src/processor.rs:1843` onward).
   b. `Deposit`, which triggers `calc_take_pnl` using the now-skewed `total_pc_without_take_pnl`/`total_coin_without_take_pnl` as `x1`/`y1` (`program/src/processor.rs:1148-1173`), altering both the pnl skim amount and the `mint_lp_amount` computed from `InvariantPool::exchange_token_to_pool` (`program/src/processor.rs:1244-1250`).
   c. A reverse swap instruction restoring the vault ratio, paying only the swap fee.
2. Compare LP tokens minted/pnl allocated in this sandwich scenario versus a baseline deposit at the pre-manipulation ratio to demonstrate the divergence in value extracted from/allocated to the pool relative to other LPs.

### Citations

**File:** program/src/processor.rs (L159-167)
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
```

**File:** program/src/processor.rs (L205-262)
```rust
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
```

**File:** program/src/processor.rs (L1148-1164)
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
```

**File:** program/src/processor.rs (L1197-1250)
```rust
        let deduct_pc_amount;
        let deduct_coin_amount;
        let mint_lp_amount;
        if deposit.base_side == 0 {
            // base coin
            deduct_pc_amount = invariant
                .exchange_coin_to_pc(deposit.max_coin_amount, RoundDirection::Ceiling)
                .ok_or(AmmError::CalculationExRateFailure)?;
            deduct_coin_amount = deposit.max_coin_amount;
            if deduct_pc_amount > deposit.max_pc_amount {
                encode_ray_log(DepositLog {
                    log_type: LogType::Deposit.into_u8(),
                    max_coin: deposit.max_coin_amount,
                    max_pc: deposit.max_pc_amount,
                    base: deposit.base_side,
                    pool_coin: total_coin_without_take_pnl,
                    pool_pc: total_pc_without_take_pnl,
                    pool_lp: amm.lp_amount,
                    calc_pnl_x: target_orders.calc_pnl_x,
                    calc_pnl_y: target_orders.calc_pnl_y,
                    deduct_coin: deduct_coin_amount,
                    deduct_pc: deduct_pc_amount,
                    mint_lp: 0,
                });
                return Err(AmmError::ExceededSlippage.into());
            }
            // base coin, check other_amount_min if need
            if deposit.other_amount_min.is_some() {
                if deduct_pc_amount < deposit.other_amount_min.unwrap() {
                    encode_ray_log(DepositLog {
                        log_type: LogType::Deposit.into_u8(),
                        max_coin: deposit.max_coin_amount,
                        max_pc: deposit.max_pc_amount,
                        base: deposit.base_side,
                        pool_coin: total_coin_without_take_pnl,
                        pool_pc: total_pc_without_take_pnl,
                        pool_lp: amm.lp_amount,
                        calc_pnl_x: target_orders.calc_pnl_x,
                        calc_pnl_y: target_orders.calc_pnl_y,
                        deduct_coin: deduct_coin_amount,
                        deduct_pc: deduct_pc_amount,
                        mint_lp: 0,
                    });
                    return Err(AmmError::ExceededSlippage.into());
                }
            }
            // coin_amount/ (total_coin_amount + coin_amount)  = output / (lp_mint.supply + output) =>  output = coin_amount / total_coin_amount * lp_mint.supply
            let invariant_coin = InvariantPool {
                token_input: deduct_coin_amount,
                token_total: total_coin_without_take_pnl,
            };
            mint_lp_amount = invariant_coin
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
```
