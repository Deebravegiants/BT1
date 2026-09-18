This confirms the analog. The `Deposit` instruction computes `deduct_pc_amount`/`deduct_coin_amount`/`mint_lp_amount` from live vault balances read at execution time <cite repo="AYontt/raydium-amm--015" path="program/src/processor.rs" start="1138="1153" />, so any attacker able to shift `amm_coin_vault`/`amm_pc_vault` balances immediately before the depositor's transaction lands (e.g., via a `SwapBaseIn`/`SwapBaseOut` in the same slot/front-run) changes the exchange rate the deposit is priced at. The `other_amount_min` slippage guard that could stop this is `Option<u64>` and is only enforced `if deposit.other_amount_min.is_some()` [1](#0-0) [2](#0-1) ; when the client omits it (unpacked as `None` whenever the instruction data is short by 8 bytes) [3](#0-2) , the deposit executes with zero slippage protection.

### Title
Missing mandatory slippage protection on `Deposit` allows sandwich attack on liquidity providers - (File: `program/src/processor.rs`, `program/src/instruction.rs`)

### Summary
The `Deposit` instruction accepts an *optional* `other_amount_min` parameter used to bound the counter-asset amount required. When this parameter is omitted (`None`), `process_deposit` performs no slippage check at all, pricing the deposit purely off the AMM vault balances read at execution time. This mirrors exactly the reported VectorBonding sandwich bug: a swap/liquidity operation without enforced slippage bounds priced on a manipulable spot reserve.

### Finding Description
`process_deposit` computes the exchange rate for a `Deposit` using `total_pc_without_take_pnl`/`total_coin_without_take_pnl`, derived from the *current* `amm_coin_vault`/`amm_pc_vault` token balances at the moment the instruction executes [4](#0-3) . Based on `deposit.base_side`, it computes `deduct_pc_amount`/`deduct_coin_amount` via `InvariantToken::exchange_coin_to_pc`/`exchange_pc_to_coin` [5](#0-4) , and only checks `other_amount_min` if it `is_some()`: [6](#0-5) 

The `other_amount_min` field is declared as `Option<u64>` in `DepositInstruction` [7](#0-6) , and the deserializer treats it as `None` whenever fewer than 8 trailing bytes remain in the instruction payload [3](#0-2) . There is no protocol-level requirement forcing a caller (or a front-end building this instruction) to supply a non-`None` value — the check exists only in the branch guarded by `.is_some()`.

Because Raydium is a constant-product/openbook-hybrid AMM where `SwapBaseIn`/`SwapBaseOut`/`SwapBaseInV2`/`SwapBaseOutV2` can move `amm_coin_vault`/`amm_pc_vault` balances arbitrarily within the same block by any unprivileged trader (subject only to `minimum_amount_out`/`max_amount_in` on the swapper's own side, not on third parties) [8](#0-7) , an attacker can:
1. Front-run a pending `Deposit` transaction that omits `other_amount_min` with a large `SwapBaseIn`, skewing the coin/pc ratio in the pool.
2. Let the victim's `Deposit` execute at the skewed ratio — since `deduct_pc_amount`/`deduct_coin_amount`/`mint_lp_amount` are all derived from the manipulated `total_pc_without_take_pnl`/`total_coin_without_take_pnl`, the victim either overpays the counter-asset relative to fair value or receives fewer LP tokens than the pre-manipulation price implied.
3. Back-run with the reverse swap, restoring the pool price and extracting the value taken from the victim's deposit, functionally identical to the WETHTOLP sandwich described in the external report.

### Impact Explanation
A successful sandwich transfers value from the depositing liquidity provider to the attacker: the victim's deposited coin/pc tokens are exchanged into LP shares at a manipulated price, and the attacker profits from the round-trip swap financed by the victim's mispriced deposit. This is a direct theft of user funds reachable by any unprivileged actor submitting ordinary `SwapBaseIn`/`SwapBaseOut` and `Deposit` instructions in a single attacker-controlled transaction bundle, with no privileged signer or off-chain component required.

### Likelihood Explanation
Exploitability depends entirely on whether the depositor's client/front-end sets `other_amount_min`. Any integration, bot, or manually constructed instruction that omits this optional field (which the on-chain program permits without warning) is unconditionally exposed. Given the field is optional at the protocol level rather than mandatory, the likelihood of some callers omitting it is non-trivial, and the attack requires only ordinary swap/deposit instructions available to any trader — no elevated privileges or unusual preconditions.

### Recommendation
Make slippage protection on `Deposit` (and symmetrically on `Withdraw`, whose `min_coin_amount`/`min_pc_amount` are similarly `Option<u64>`) mandatory rather than optional at the instruction-decoding layer, so `process_deposit`/`process_withdraw` reject any instruction payload that omits the bound instead of silently skipping the check. Alternatively/additionally, consider using a TWAP or otherwise more manipulation-resistant reference price rather than the instantaneous vault balances for computing deposit exchange rates.

### Proof of Concept
1. Attacker submits a bundle/single transaction containing:
   - `SwapBaseIn` with a large `amount_in` of pc (or coin) and a `minimum_amount_out` set to the attacker's own break-even, shifting `amm_pc_vault`/`amm_coin_vault` balances and thus `total_pc_without_take_pnl`/`total_coin_without_take_pnl` [9](#0-8) .
   - The victim's pending `Deposit` instruction (built by a client that left `other_amount_min = None`), which now executes against the skewed ratio computed in `process_deposit` [10](#0-9) , minting LP tokens/deducting counter-asset at the manipulated price with the `other_amount_min` check absent (`deposit.other_amount_min.is_some()` is `false`) [11](#0-10) .
   - A reverse `SwapBaseIn`/`SwapBaseOut` restoring the original ratio, realizing the attacker's profit taken from the victim's deposit.
2. Net effect: attacker's pre/post balance shows profit; victim receives LP tokens/deducted amounts inconsistent with the pre-manipulation fair price, exactly mirroring the reported bonding-contract sandwich exploit.

### Citations

**File:** program/src/processor.rs (L1138-1153)
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
```

**File:** program/src/processor.rs (L1197-1256)
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
        } else {
            // base pc
            deduct_coin_amount = invariant
                .exchange_pc_to_coin(deposit.max_pc_amount, RoundDirection::Ceiling)
                .ok_or(AmmError::CalculationExRateFailure)?;
            deduct_pc_amount = deposit.max_pc_amount;
```

**File:** program/src/processor.rs (L1274-1293)
```rust
            // base pc, check other_amount_min if need
            if deposit.other_amount_min.is_some() {
                if deduct_coin_amount < deposit.other_amount_min.unwrap() {
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
```

**File:** program/src/processor.rs (L1940-1996)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        let swap_direction;
        if user_source.mint == amm_coin_vault.mint && user_destination.mint == amm_pc_vault.mint {
            swap_direction = SwapDirection::Coin2PC
        } else if user_source.mint == amm_pc_vault.mint
            && user_destination.mint == amm_coin_vault.mint
        {
            swap_direction = SwapDirection::PC2Coin
        } else {
            return Err(AmmError::InvalidUserToken.into());
        }
        if user_source.amount < swap.amount_in {
            encode_ray_log(SwapBaseInLog {
                log_type: LogType::SwapBaseIn.into_u8(),
                amount_in: swap.amount_in,
                minimum_out: swap.minimum_amount_out,
                direction: swap_direction as u64,
                user_source: user_source.amount,
                pool_coin: total_coin_without_take_pnl,
                pool_pc: total_pc_without_take_pnl,
                out_amount: 0,
            });
            return Err(AmmError::InsufficientFunds.into());
        }
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

**File:** program/src/instruction.rs (L56-65)
```rust
#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct DepositInstruction {
    /// Pool token amount to transfer. token_a and token_b amount are set by
    /// the current exchange rate and size of the pool
    pub max_coin_amount: u64,
    pub max_pc_amount: u64,
    pub base_side: u64,
    pub other_amount_min: Option<u64>,
}
```

**File:** program/src/instruction.rs (L355-371)
```rust
            3 => {
                let (max_coin_amount, rest) = Self::unpack_u64(rest)?;
                let (max_pc_amount, rest) = Self::unpack_u64(rest)?;
                let (base_side, rest) = Self::unpack_u64(rest)?;
                let other_amount_min = if rest.len() >= 8 {
                    let (other_amount_min, _rest) = Self::unpack_u64(rest)?;
                    Some(other_amount_min)
                } else {
                    None
                };
                Self::Deposit(DepositInstruction {
                    max_coin_amount,
                    max_pc_amount,
                    base_side,
                    other_amount_min,
                })
            }
```
