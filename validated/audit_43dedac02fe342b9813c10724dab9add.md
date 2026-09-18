### Title
Deposit/Withdraw LP share math is derived from spot vault balances with optional slippage protection, enabling same-transaction sandwich manipulation of LP minting/redemption ratios - (File: `program/src/processor.rs`)

### Summary
`process_deposit` and `process_withdraw` compute the coin/pc amounts to be exchanged for LP tokens (or vice versa) exclusively from the **current instantaneous** `amm_coin_vault.amount` / `amm_pc_vault.amount` balances read inside the instruction itself [1](#0-0) . There is no TWAP, oracle, or any mechanism resistant to intra-transaction manipulation, and both the deposit's `other_amount_min` and the withdraw's `min_coin_amount`/`min_pc_amount` slippage guards are `Option<u64>` fields that are only enforced when the caller chooses to supply them [2](#0-1) [3](#0-2) [4](#0-3) . This mirrors the report's root cause — LP-share pricing computed from a value that can diverge from the "true" pool price within a short window, combined with weak/optional slippage enforcement, letting an attacker realize the divergence at the expense of other LPs.

### Finding Description
`process_deposit` reads live vault balances, subtracts any pending `need_take_pnl_*`, and builds an `InvariantToken`/`InvariantPool` purely off that spot state [5](#0-4) . Depending on `base_side`, one side's amount is fixed by the caller and the other side (and the LP amount to mint) is derived proportionally from these spot reserves [6](#0-5) . The only protections are:
- `deduct_pc_amount > deposit.max_pc_amount` → revert (bounds cost, not fairness of ratio) [7](#0-6) .
- `other_amount_min` check, which is entirely skipped if the field is `None` [8](#0-7) .

Symmetrically, `process_withdraw` computes `coin_amount`/`pc_amount` from `InvariantPool` built on the same spot-read vault balances [9](#0-8) , and its slippage check only fires when **both** `min_coin_amount` and `min_pc_amount` are supplied [4](#0-3) .

Because Solana executes all instructions of a transaction atomically, an attacker can compose, in a single attacker-submitted transaction:
1. A `SwapBaseIn`/`SwapBaseOut` instruction that shifts `total_coin_without_take_pnl`/`total_pc_without_take_pnl` away from the pool's fair/expected ratio (spot price is fully attacker-influenced within the tx since it's directly derived from vault token balances, exactly as used in the swap math itself) [10](#0-9) .
2. A `Deposit` (with `other_amount_min = None`, or `Withdraw` with the mins omitted) that mints LP (or redeems coin/pc) at the now-skewed ratio.
3. A reverse swap restoring the pool to its prior state.

Since `mint_lp_amount` / `coin_amount,pc_amount` are computed strictly from the ratio present at the moment the instruction executes [11](#0-10) [12](#0-11) , the attacker can mint disproportionately many LP tokens for a given contribution (diluting existing LPs) or extract disproportionately more of one asset on withdrawal, then reverse the price-moving swap to walk away net-positive — all inside one transaction, with no reliance on a privileged signer or off-chain component. This is directly analogous to the report's core issue: computing share/price from a value that doesn't reflect the "actual" equilibrium price of the pool, compounded by optional (and thus bypassable) slippage protection.

### Impact Explanation
An attacker can dilute or drain value from existing liquidity providers by minting LP tokens at a manipulated ratio or by withdrawing more of a given asset than their true pro-rata share, using a single self-contained transaction. This is a realizable value-transfer from LPs to attacker (fund theft / mispriced LP minting), which is a Medium/High-severity issue depending on achievable price impact and pool depth.

### Likelihood Explanation
Likelihood is high for shallow or low-liquidity pools: no privileged access is needed, all accounts (`amm_info`, vaults, `target_orders`) are attacker-selectable to a legitimate pool, `other_amount_min`/`min_coin_amount`/`min_pc_amount` can simply be omitted by the client building the instruction, and Solana's atomic multi-instruction transactions make the swap→deposit/withdraw→reverse-swap sequence trivial to construct.

### Recommendation
- Make slippage protection on `Deposit` (`other_amount_min`) and `Withdraw` (`min_coin_amount`, `min_pc_amount`) mandatory rather than `Option`, or enforce a program-side minimum protection regardless of caller input.
- Consider time-weighted or previous-slot reserve snapshots (rather than same-instruction spot reserves) for LP-share pricing, or bound the maximum allowed reserve-ratio deviation from a reference price within a transaction/slot.
- Reject Deposit/Withdraw instructions that appear in the same transaction as a Swap instruction touching the same AMM (or otherwise rate-limit ratio changes within a transaction).

### Proof of Concept
1. Attacker submits one transaction with three instructions against the same `AmmInfo`/vaults:
   - `SwapBaseIn` (large size) that shifts `amm_coin_vault.amount`/`amm_pc_vault.amount` far from the pre-tx ratio [10](#0-9) .
   - `Deposit` with `other_amount_min = None`, `base_side` chosen so `deduct_*`/`mint_lp_amount` are computed off the skewed `total_coin_without_take_pnl`/`total_pc_without_take_pnl` [6](#0-5) , minting more LP than the attacker's contribution is fairly worth.
   - A reverse `SwapBaseIn`/`SwapBaseOut` restoring the pool price, leaving the attacker holding LP tokens redeemable for more value than deposited, at other LPs' expense.
2. All three instructions execute atomically; no revert occurs because `other_amount_min` is `None` and `max_coin_amount`/`max_pc_amount` bounds are satisfied by construction.

### Citations

**File:** program/src/processor.rs (L1138-1177)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        let user_source_coin =
            Self::unpack_token_account(&user_source_coin_info, spl_token_program_id)?;
        let user_source_pc =
            Self::unpack_token_account(&user_source_pc_info, spl_token_program_id)?;
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;
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
        let invariant = InvariantToken {
            token_coin: total_coin_without_take_pnl,
            token_pc: total_pc_without_take_pnl,
        };
```

**File:** program/src/processor.rs (L1200-1250)
```rust
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

**File:** program/src/processor.rs (L1719-1761)
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

**File:** program/src/processor.rs (L1779-1786)
```rust
        if coin_amount < amm_coin_vault.amount && pc_amount < amm_pc_vault.amount {
            if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some() {
                if withdraw.min_coin_amount.unwrap() > coin_amount
                    || withdraw.min_pc_amount.unwrap() > pc_amount
                {
                    return Err(AmmError::ExceededSlippage.into());
                }
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

**File:** program/src/instruction.rs (L58-75)
```rust
pub struct DepositInstruction {
    /// Pool token amount to transfer. token_a and token_b amount are set by
    /// the current exchange rate and size of the pool
    pub max_coin_amount: u64,
    pub max_pc_amount: u64,
    pub base_side: u64,
    pub other_amount_min: Option<u64>,
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct WithdrawInstruction {
    /// Pool token amount to transfer. token_a and token_b amount are set by
    /// the current exchange rate and size of the pool
    pub amount: u64,
    pub min_coin_amount: Option<u64>,
    pub min_pc_amount: Option<u64>,
}
```
