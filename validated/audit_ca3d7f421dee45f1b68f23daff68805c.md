### Title
Optional (omittable) slippage parameters in `Deposit`/`Withdraw` instructions allow front-run/sandwich attacks on liquidity providers - (File: `program/src/processor.rs`, `program/src/instruction.rs`)

### Summary
The `Deposit` and `Withdraw` instructions accept slippage-protection fields (`other_amount_min`, `min_coin_amount`, `min_pc_amount`) as `Option<u64>` that are parsed conditionally based on instruction-data length, and the processor only enforces the check when the caller chose to include them. When they are omitted, the effect is identical to the sNOTE.sol bug: the acceptable minimum is implicitly `0`, so any unprivileged actor can front-run a depositor's or withdrawer's transaction to shift the pool ratio and capture value from them.

### Finding Description
`AmmInstruction::unpack` for `Deposit` (tag `3`) only decodes `other_amount_min` if there happen to be at least 8 extra bytes in the instruction data; otherwise it is `None`: [1](#0-0) 

Likewise for `Withdraw` (tag `4`), `min_coin_amount`/`min_pc_amount` are only decoded if 16 extra bytes are present, otherwise both default to `None`: [2](#0-1) 

In `process_deposit`, the slippage check that guards against an unfavorable exchange ratio is only executed `if deposit.other_amount_min.is_some()`. If the field is `None` (i.e. the instruction was built without appending the optional bytes), the check is skipped entirely and the deposit proceeds at whatever ratio the pool happens to be at when the transaction lands: [3](#0-2) [4](#0-3) 

Similarly, in `process_withdraw`, the check on `min_coin_amount`/`min_pc_amount` only fires `if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some()`; if either is `None`, the withdrawal is executed unconditionally against the current, potentially manipulated pool ratio: [5](#0-4) 

This is structurally the same defect as sNOTE.sol's `_mintFromAssets()` hardcoding `minimumBPT = 0`: the slippage guard exists in the code but is not mandatory, so it defaults to "accept any amount" whenever the caller (a wallet, SDK, or the CLI shown in the README, which calls `deposit()`/`withdraw()` without always supplying the optional min amounts) omits it. Any unprivileged party watching the transaction pool can insert swap transactions immediately before and after the victim's `Deposit`/`Withdraw` in the same slot to shift `total_coin_without_take_pnl`/`total_pc_without_take_pnl`, causing the victim to mint fewer LP tokens than expected on deposit, or receive fewer underlying tokens than expected on withdrawal, while the attacker's sandwich extracts the difference. Note the swap instructions (`SwapBaseIn`/`SwapBaseOut`) do NOT have this weakness — their `minimum_amount_out`/`max_amount_in` are unconditionally required fields, so the design intent is that all endpoints enforce slippage — but `Deposit`/`Withdraw` regressed that intent by making it optional.

### Impact Explanation
An attacker with no privileges can, within the reachable path of a single submitted transaction pair (front-run + back-run) around a victim's `Deposit` or `Withdraw` call, extract value at the expense of a legitimate liquidity provider or withdrawer whenever the min-amount fields are omitted. This is a direct value-transfer/theft vector against user funds, consistent with Medium severity per the analogous, already-confirmed Notional finding.

### Likelihood Explanation
Likelihood is meaningful but conditional on client behavior: any integrator or user who calls `deposit()`/`withdraw()` (as documented in the README example, which does not show the optional min fields being set) without explicitly supplying `other_amount_min`/`min_coin_amount`/`min_pc_amount` is exposed on every such call, on every pool, to sandwich attacks by any MEV searcher monitoring the mempool/leader schedule.

### Recommendation
Make the slippage-protection fields mandatory (non-`Option`) for both `Deposit` and `Withdraw`, matching the design already used for `SwapBaseIn`/`SwapBaseOut`, so the check in `process_deposit`/`process_withdraw` cannot be bypassed by simply omitting the trailing bytes from the instruction data.

### Proof of Concept
1. Attacker observes a pending `Deposit` instruction from a victim that was built without the optional `other_amount_min` bytes (`instruction.rs` tag `3` decode path leaves it `None`).
2. Attacker submits a large swap in the same block immediately before the victim's deposit to skew `total_coin_without_take_pnl`/`total_pc_without_take_pnl`, then the victim's deposit executes with `deposit.other_amount_min.is_some()` false, so the check at `program/src/processor.rs:1224-1242`/`1274-1293` is skipped and the victim deposits at the skewed ratio, receiving less `mint_lp_amount` than they would at the fair price.
3. Attacker reverses the swap right after, restoring the pool price and pocketing the difference. The same pattern applies symmetrically to `Withdraw` via the unguarded `program/src/processor.rs:1779-1786` path when `min_coin_amount`/`min_pc_amount` are `None`.

### Citations

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

**File:** program/src/instruction.rs (L372-386)
```rust
            4 => {
                let (amount, rest) = Self::unpack_u64(rest)?;
                let (min_coin_amount, min_pc_amount) = if rest.len() >= 16 {
                    let (min_coin_amount, rest) = Self::unpack_u64(rest)?;
                    let (min_pc_amount, _rest) = Self::unpack_u64(rest)?;
                    (Some(min_coin_amount), Some(min_pc_amount))
                } else {
                    (None, None)
                };
                Self::Withdraw(WithdrawInstruction {
                    amount,
                    min_coin_amount,
                    min_pc_amount,
                })
            }
```

**File:** program/src/processor.rs (L1223-1242)
```rust
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
