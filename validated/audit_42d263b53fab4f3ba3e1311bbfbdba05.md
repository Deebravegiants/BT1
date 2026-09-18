### Title
Optional (unenforced) slippage protection in `Withdraw`/`Deposit` allows unprotected LP exits to be sandwiched - (File: `program/src/processor.rs`, `program/src/instruction.rs`)

### Summary
The external report flags that Connext's `_xcall()` does not require a delegate address, so a transaction with no configured recovery/slippage-fix mechanism can permanently lose funds if destination conditions turn unfavorable. The analogous pattern in this AMM program is that the `Withdraw` and `Deposit` instructions accept **optional** slippage-protection fields (`min_coin_amount`/`min_pc_amount` for withdraw, `other_amount_min` for deposit) that the on-chain program never requires to be present. If they are omitted, the corresponding check is entirely skipped, and the transfer executes unconditionally at whatever ratio the pool happens to be at when the instruction lands.

### Finding Description
`AmmInstruction::unpack` treats the withdraw slippage bounds as fully optional trailing bytes: if the instruction data is shorter than 16 extra bytes, both `min_coin_amount` and `min_pc_amount` are set to `None` with no error. [1](#0-0) 

The same pattern exists for `Deposit`'s `other_amount_min`. [2](#0-1) 

In `process_withdraw`, the slippage check is only executed `if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some()`. When both are `None` (i.e., the caller supplied the short 9-byte payload), the coin/pc transfer amounts computed from the *current* pool ratio are sent out with **no** bound check at all: [3](#0-2) 

Similarly, `process_deposit` only enforces `other_amount_min` `if deposit.other_amount_min.is_some()`: [4](#0-3) [5](#0-4) 

There is no requirement anywhere in `process_withdraw`/`process_deposit` (or in `AmmInstruction::unpack`) that these protective fields be present — exactly mirroring the reported bug class: an optional safety mechanism exists, but its presence is never enforced by the protocol, so a submitter (or a wallet/SDK that fails to populate it) can silently disable it.

### Impact Explanation
Because the check is skipped entirely (not just relaxed) when the fields are absent, an LP withdrawal or deposit submitted without slippage bounds is fully exposed to sandwich/front-running: an attacker can submit a swap instruction immediately before the victim's unprotected `Withdraw`/`Deposit` in the same block, shifting `total_pc_without_take_pnl`/`total_coin_without_take_pnl` unfavorably, then let the victim's transaction execute at the manipulated ratio. This results in concrete, permanent loss of LP funds (the victim receives fewer/less valuable tokens than the fair-market ratio), matching the "concrete theft or permanent freezing of user or LP funds" acceptance bar. This is Medium risk, consistent with the original report's rating, since it depends on the caller/client choosing to omit the optional fields, but the protocol itself does nothing to prevent or flag this unsafe usage.

### Likelihood Explanation
Any unprivileged submitter can trigger this by constructing `Withdraw`/`Deposit` instruction data with the minimal (non-slippage) byte length — this is entirely attacker/caller-controlled data, requiring no privileged access. Historically, integrators/relayers/bots that build raw instruction bytes without the newer optional trailing fields (e.g., legacy clients, or simplified bots) would produce exactly this unprotected instruction shape, making exploitation realistic whenever such a transaction is visible in the mempool alongside MEV-capable actors.

### Recommendation
Make `min_coin_amount`/`min_pc_amount` (withdraw) and `other_amount_min` (deposit) mandatory rather than `Option<u64>`, or reject the instruction outright if the trailing slippage-bound bytes are missing (mirroring the report's recommendation to enforce presence or explicitly document the risk). At minimum, document clearly that omitting these fields disables slippage protection, and update all reference clients/SDKs to always populate them.

### Proof of Concept
1. Attacker observes a pending `Withdraw` transaction (tag `4`) whose instruction data is exactly 9 bytes (`tag + amount`, no trailing 16 bytes for `min_coin_amount`/`min_pc_amount`), which unpacks to `(None, None)` per `AmmInstruction::unpack` [1](#0-0) .
2. Attacker front-runs it with a `SwapBaseIn`/`SwapBaseOut` that pushes the pool's coin/pc ratio in the direction unfavorable to the pending withdrawer.
3. The victim's `Withdraw` executes with `withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some()` evaluating to `false`, so the slippage guard at [6](#0-5)  is bypassed, and `coin_amount`/`pc_amount` computed from the manipulated post-swap ratio are transferred out unconditionally.
4. Attacker back-runs with an opposite swap to restore the ratio and capture the value extracted from the victim's under-protected withdrawal.

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

**File:** program/src/processor.rs (L1779-1804)
```rust
        if coin_amount < amm_coin_vault.amount && pc_amount < amm_pc_vault.amount {
            if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some() {
                if withdraw.min_coin_amount.unwrap() > coin_amount
                    || withdraw.min_pc_amount.unwrap() > pc_amount
                {
                    return Err(AmmError::ExceededSlippage.into());
                }
            }
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_coin_vault_info.clone(),
                user_dest_coin_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                coin_amount,
            )?;
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_pc_vault_info.clone(),
                user_dest_pc_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                pc_amount,
            )?;
```
