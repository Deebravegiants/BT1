### Title
Instantaneous Spot-Price Used for PnL Separation Allows Same-Transaction Price Manipulation to Divert Protocol PnL into LP Withdrawals - (File: `program/src/processor.rs`)

### Summary
`calc_take_pnl` computes the trading-fee "pnl" that must be skimmed into the protocol's `need_take_pnl_pc`/`need_take_pnl_coin` reserve by comparing the pool's *current, single-block spot reserve ratio* against a previously recorded baseline (`target.calc_pnl_x` / `target.calc_pnl_y`). There is no time-weighting (TWAP) or manipulation-resistance on this "current price" input — it is read directly from the live AMM vault balances at the moment the instruction executes.

### Finding Description
`calc_take_pnl` derives the amount of accumulated trading-fee profit ("pnl") to reserve for the protocol by using the *current* pool reserves `x1`/`y1` as the "current price" reference: [1](#0-0) 

It computes `x2_power = calc_x_power(target.calc_pnl_x, target.calc_pnl_y, x1, y1)` and derives `x2`, `y2` from that, then computes `delta_x = x1 - x2`, `delta_y = y1 - y2` (scaled by `pnl_numerator/pnl_denominator`) as the amount to move into the pnl reserve: [2](#0-1) 

Because `x1`/`y1` are computed directly from the live `amm_coin_vault`/`amm_pc_vault` token balances in the *same instruction* that calls `calc_take_pnl` (via `calc_total_without_take_pnl_no_orderbook` immediately followed by `normalize_decimal_v2`), an attacker who controls the ordering of instructions within a single transaction can temporarily skew the spot ratio just before this calculation runs: [3](#0-2) 

`process_withdraw` — reachable by any unprivileged LP holder — calls `calc_take_pnl` with the live spot ratio and then immediately uses the *post-pnl-deduction* `total_pc_without_take_pnl`/`total_coin_without_take_pnl` to compute the withdrawer's `coin_amount`/`pc_amount` via `InvariantPool::exchange_pool_to_token`: [4](#0-3) 

This is precisely the bug class described in the report: a price value used for accounting is taken as a single point-in-time (spot) read rather than a time-weighted average, making it manipulable within the attacker's own transaction. In Raydium's case the manipulable input is not an external price oracle but the AMM's own reserve ratio, which is directly moved by the four swap instructions (`process_swap_base_in`/`_out`, and their `_v2` variants) that operate on the very same `amm_coin_vault`/`amm_pc_vault` accounts: [5](#0-4) 

### Impact Explanation
By composing, in a single atomic transaction:
1. A large `SwapBaseIn`/`SwapBaseOut` against the pool to skew the coin/pc reserve ratio,
2. A `Withdraw` call (unprivileged, attacker-controlled LP amount) that triggers `calc_take_pnl` using the now-skewed spot ratio,
3. A reverse swap to restore the price (paying only the swap fee as cost),

an attacker can distort the `delta_x`/`delta_y` "pnl" amount computed for that withdrawal. Since a smaller (or zero) `delta_x`/`delta_y` leaves more of `total_pc_without_take_pnl`/`total_coin_without_take_pnl` available for the `InvariantPool::exchange_pool_to_token` computation that determines the withdrawer's payout, the attacker's withdrawal is computed against a reserve pool that retained value that should have been diverted to `need_take_pnl_pc`/`need_take_pnl_coin` (the protocol/LP fee-accrual reserve redeemable only by the privileged `pnl_owner` via `process_withdrawpnl`). This results in an insolvency-style leakage: value that is accounting-wise owed to the protocol's pnl reserve is instead extracted through a manipulated withdrawal, reducing what remains for other LPs and the `pnl_owner`.

### Likelihood Explanation
The precondition (attacker-chosen accounts and data, single transaction, unprivileged swapper/LP) matches exactly the instructions in scope: any of the four swap instructions plus `Withdraw`, both directly reachable without any privileged signer. The cost to the attacker is only the AMM's trading fee for the two swaps (in and out), which is bounded and can be amortized against the diverted pnl if the attacker holds a meaningful LP position and pool liquidity/fee parameters make the round-trip cost smaller than the diverted delta. This requires the attacker to hold LP tokens and time the swap-withdraw-swap sequence, which is achievable in one transaction with no special privileges.

### Recommendation
Do not use the pool's live, single-instruction spot reserve ratio as the reference "current price" for `calc_take_pnl`. Instead, base the pnl-separation price on a time-weighted or otherwise manipulation-resistant reference (e.g., an average of reserves sampled over multiple slots/instructions, or a price recorded prior to the current transaction), consistent with the remediation pattern in the referenced report (computing price from accumulated/synth amounts rather than instantaneous state). At minimum, disallow combining swap and withdraw/pnl-affecting instructions from the same signer within a single transaction, or snapshot `x1`/`y1` from state that cannot be altered earlier in the same transaction.

### Proof of Concept
Conceptual transaction (single tx, attacker-controlled):
1. `SwapBaseIn`/`SwapBaseOut` — swap a large amount of coin→pc (or pc→coin) against the target AMM to sharply move `amm_coin_vault`/`amm_pc_vault` balances, skewing the pc/coin ratio away from the value implied by `target.calc_pnl_x`/`target.calc_pnl_y`.
2. `Withdraw` — burn LP tokens; `process_withdraw` reads the now-skewed `amm_pc_vault.amount`/`amm_coin_vault.amount` as `x1`/`y1` [3](#0-2) , computes `delta_x`/`delta_y` via `calc_take_pnl` using this skewed instantaneous ratio, and then computes the attacker's `coin_amount`/`pc_amount` from `total_pc_without_take_pnl`/`total_coin_without_take_pnl` after this (manipulated) pnl deduction [4](#0-3) .
3. A reverse `SwapBaseIn`/`SwapBaseOut` restores the pool ratio, leaving the attacker with a withdrawal computed against a reserve base that improperly retained value destined for the pnl reserve, at the cost of only the round-trip swap fees.

Note: I was not able to inspect the exact body of `Calculator::calc_x_power` in `program/src/math.rs` in this session (only its signature/usage was retrieved), so the precise magnitude of `delta_x`/`delta_y` distortion achievable per unit of price skew could not be numerically modeled here. A background Devin session with full repository access should read `program/src/math.rs`'s `calc_x_power` implementation to construct a concrete numeric PoC and quantify the extractable value versus swap-fee cost before treating this as confirmed-exploitable at a specific severity.

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

**File:** program/src/processor.rs (L1719-1748)
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

**File:** program/src/processor.rs (L1970-1996)
```rust
        let swap_fee = U128::from(swap.amount_in)
            .checked_mul(amm.fees.swap_fee_numerator.into())
            .unwrap()
            .checked_ceil_div(amm.fees.swap_fee_denominator.into())
            .unwrap();
        let swap_in_after_deduct_fee = U128::from(swap.amount_in).checked_sub(swap_fee).unwrap();
        let swap_amount_out = Calculator::swap_token_amount_base_in(
            swap_in_after_deduct_fee,
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        )
        .as_u64();
        encode_ray_log(SwapBaseInLog {
            log_type: LogType::SwapBaseIn.into_u8(),
            amount_in: swap.amount_in,
            minimum_out: swap.minimum_amount_out,
            direction: swap_direction as u64,
            user_source: user_source.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            out_amount: swap_amount_out,
        });
        if swap_amount_out < swap.minimum_amount_out {
            return Err(AmmError::ExceededSlippage.into());
        }
        if swap_amount_out == 0 || swap.amount_in == 0 {
```
