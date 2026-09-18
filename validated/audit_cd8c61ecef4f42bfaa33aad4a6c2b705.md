## Title
`Processor::calc_take_pnl` uses manipulable instantaneous pool reserves as a spot-price oracle for PnL skimming, allowing single-transaction price-manipulation to distort LP withdrawal/deposit accounting - (`program/src/processor.rs`)

## Summary
`Processor::calc_take_pnl`, invoked from `process_deposit`, `process_withdraw`, and `process_withdrawpnl`, computes how much of the pool's token balances constitute "pnl" to be skimmed to the protocol using the **current spot ratio** of the live vault balances (`x1`/`y1`), exactly like the reported `USSDRebalancer.getOwnValuation()` bug that used the current AMM spot price. Because a single Solana transaction can chain a `SwapBaseIn`/`SwapBaseOut` instruction immediately before a `Deposit`/`Withdraw` instruction on the same pool, an unprivileged attacker can transiently skew the vault ratio, causing `calc_take_pnl` to compute a distorted pnl split, and then reverse the swap in the same atomic transaction.

## Finding Description
`calc_take_pnl` derives the "current price" purely from the AMM's live vault balances: [1](#0-0) 

It computes `x2 = sqrt(last_k * current_price)` and derives `y2` from it, then skims `delta_x`/`delta_y` (scaled by `pnl_numerator/pnl_denominator`) into `amm.state_data.need_take_pnl_pc/coin`, and correspondingly reduces `total_pc_without_take_pnl`/`total_coin_without_take_pnl`: [2](#0-1) 

`x1`/`y1` (the "current_x"/"current_y") are computed fresh, every call, straight from the live `amm_coin_vault`/`amm_pc_vault` SPL token account balances read at instruction execution time: [3](#0-2) 

There is no TWAP, checkpointing, or same-block/same-slot manipulation guard — the ratio is read directly from whatever the vault balances are at the moment the instruction executes. `Withdraw`, `Deposit`, and `WithdrawPnl` are all reachable by any signer holding LP tokens (or none, for withdrawpnl calling by a permissioned pnl-owner, but Withdraw/Deposit are fully open to unprivileged users), and Solana allows an attacker to place a `SwapBaseIn`/`SwapBaseOut` instruction on the same pool immediately before the `Withdraw`/`Deposit` instruction, and a reversing swap immediately after, all within one atomic transaction and one submitted signature.

The subsequent withdraw math then divides the **post-pnl-skim** totals proportionally by the withdrawn LP share: [4](#0-3) 

Because the attacker controls the instantaneous ratio fed into `calc_take_pnl`, they can drive `x2`/`y2` toward `x1`/`y1` (minimizing `diff_x`/`diff_y`, i.e., minimizing `pc_pnl_amount`/`coin_pnl_amount` skimmed to the protocol) or push the split in whichever direction benefits their own withdrawal/deposit ratio in that same instruction, then restore the pool price with a reversing swap. The persisted baseline `target_orders.calc_pnl_x`/`calc_pnl_y` is also updated using these manipulated totals, corrupting the checkpoint for all subsequent calls: [5](#0-4) 

This is structurally identical to the reported bug class: a spot/instantaneous reserve ratio, obtainable and moved by the attacker within the scope of a single transaction (flashswap-equivalent), is used directly as an oracle input to a critical accounting computation (`getOwnValuation`'s current-price-based rebalance decision vs. `calc_take_pnl`'s current-price-based pnl split), without any manipulation-resistant mechanism (Chainlink/TWAP), enabling the attacker to bias the accounting outcome in their favor before reverting the price.

## Impact Explanation
An attacker who holds LP tokens (or acquires/returns them within the same transaction) can:
1. Swap a large amount of one side into the pool to skew the coin/pc ratio.
2. Call `Withdraw` (or `Deposit`) in the same transaction — `calc_take_pnl` computes the pnl skim using the skewed ratio, reducing the amount diverted to `need_take_pnl_pc/coin` (the protocol's fee accrual) and leaving proportionally more of the real vault balance in `total_pc_without_take_pnl`/`total_coin_without_take_pnl`, which the attacker's LP burn then claims a share of.
3. Reverse the initial swap to restore the pool price, paying only the swap fee for the round trip.

This lets an unprivileged actor systematically siphon value that should have accrued to the protocol's pnl bucket (`need_take_pnl_pc/coin`, later drained via `process_withdrawpnl`) and distort the checkpoint (`target_orders.calc_pnl_x/y`) used by every future pnl computation, degrading pool accounting integrity for all subsequent LPs. This satisfies "insolvent pool accounting" / unauthorized value extraction from protocol-level accounting.

## Likelihood Explanation
High reachability: `Deposit`/`Withdraw` require only a signer holding LP tokens and standard accounts (no privileged role), and `SwapBaseIn`/`SwapBaseOut` are fully public. Combining them into a single transaction with attacker-chosen swap size is straightforward and costs only swap fees plus temporary capital (which can be sized to the attacker's own funds since no flash loan is even strictly required if the attacker already provides both swap legs).

## Recommendation
Do not derive the pnl-skim ratio from the vault's instantaneous balance at instruction time. Use a manipulation-resistant reference (e.g., a TWAP computed from accumulated volume/time, or restrict pnl-taking to only being triggered outside of the same transaction as any swap on the pool, or bound the maximum price deviation allowed between the checkpointed `calc_pnl_x/y` ratio and the current ratio before allowing a pnl skim to proceed).

## Proof of Concept
1. Pool state: `coin_vault = C`, `pc_vault = P`, `target_orders.calc_pnl_x/y` reflecting a stored baseline ratio.
2. Attacker submits a single transaction containing:
   - Instruction A: `SwapBaseIn` (large amount) shifting the vault ratio to `C'`, `P'`.
   - Instruction B: `Withdraw` burning attacker's LP tokens — `calc_take_pnl` uses `x1=P'`, `y1=C'` (the manipulated ratio) to compute `delta_x`/`delta_y`, reducing (or otherwise skewing) `pc_pnl_amount`/`coin_pnl_amount` skimmed to `need_take_pnl_pc/coin`; the attacker's `coin_amount`/`pc_amount` withdrawal is computed from the resulting `total_pc_without_take_pnl`/`total_coin_without_take_pnl`.
   - Instruction C: `SwapBaseIn`/`SwapBaseOut` reversing the initial swap, restoring the pool close to its original ratio (minus swap fees).
3. Net effect: the attacker's withdrawal captures a larger share of the pool's real token balances than the un-manipulated ratio would have allowed, while `need_take_pnl_pc/coin` (protocol pnl accrual) is reduced, and `target_orders.calc_pnl_x/y` is checkpointed using the manipulated totals — corrupting the baseline used by all future `calc_take_pnl` invocations.

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

**File:** program/src/processor.rs (L196-262)
```rust
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
```

**File:** program/src/processor.rs (L1719-1735)
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

**File:** program/src/processor.rs (L1818-1838)
```rust
        // step4: update target_orders.calc_pnl_x & target_orders.calc_pnl_y
        target_orders.calc_pnl_x = x1
            .checked_sub(Calculator::normalize_decimal_v2(
                pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_sub(Calculator::normalize_decimal_v2(
                coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
```
