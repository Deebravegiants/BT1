### Title
Withdraw/Deposit Slippage Protection Is Optional and Silently Skipped When Omitted, Exposing Users to Sandwich/Front-Running Losses - (File: `program/src/processor.rs`, `program/src/instruction.rs`)

### Summary
The `Deposit` and `Withdraw` instructions in the Raydium AMM program accept slippage-protection parameters (`min_coin_amount`/`min_pc_amount` for withdraw, `other_amount_min` for deposit) as `Option<u64>` rather than mandatory values. When a user (or a wallet/integration that mis-serializes the instruction) omits these parameters, the program performs **no** slippage check at all before transferring tokens or minting/burning LP, exposing the user to receiving far fewer tokens (on withdraw) or depositing at a worse ratio (on deposit) than expected if the pool's coin/pc ratio shifts between transaction submission and execution.

### Finding Description
`WithdrawInstruction` and `DepositInstruction` both declare their slippage-bound fields as optional: [1](#0-0) 

The unpacking logic explicitly allows omitting these fields — if the remaining instruction data is too short, `min_coin_amount`/`min_pc_amount` (or `other_amount_min`) are simply set to `None`: [2](#0-1) 

In `process_withdraw`, the slippage check is guarded by an `is_some()` condition on both fields; if either is `None`, the check is skipped entirely and the transfer/burn proceeds unconditionally: [3](#0-2) 

Similarly, in `process_deposit`, the `other_amount_min` check is only performed `if deposit.other_amount_min.is_some()`, meaning a caller can bypass protection on the non-base side of the deposit: [4](#0-3) [5](#0-4) 

This mirrors the root cause in the external report: the withdraw/deposit exchange ratio (`total_coin_without_take_pnl` / `total_pc_without_take_pnl` versus `amm.lp_amount`) is computed live inside the instruction using current vault balances and the on-chain PNL take (`calc_take_pnl`), and can shift due to concurrent swaps, deposits/withdrawals from other users, or admin PNL withdrawal (`WithdrawPnl`) landing before the user's transaction. Because the protection fields are optional and default to `None` when the data is short, any transaction that omits them (whether by user choice, wallet bug, or an attacker constructing a transaction on behalf of a victim's approved delegate/session) is executed with zero slippage protection, unlike swap instructions where `minimum_amount_out`/`max_amount_in` are mandatory, non-optional fields: [6](#0-5) 

### Impact Explanation
A user withdrawing LP or depositing coin/pc without specifying the optional min/max bounds can have their transaction sandwiched: an attacker observes the pending withdraw/deposit in the mempool, executes a swap (or triggers a PNL take) that shifts `total_coin_without_take_pnl`/`total_coin_vault.amount` ratios, and the victim's withdraw/deposit executes at the worse ratio, resulting in a direct, quantifiable loss of user funds — analogous to the confirmed Medium finding in the referenced report. This affects any unprivileged LP calling `Withdraw` or `Deposit` without the optional parameters.

### Likelihood Explanation
Likelihood is meaningful because: (1) many client integrations/wallets historically omit optional trailing parameters for simplicity, defaulting to `None`, as shown even in this repo's own CLI (`slippage_limit: false`, `another_min_limit: false` per README examples), and (2) sandwiching a visible mempool withdraw/deposit transaction requires only a single attacker-controlled swap transaction with no privileged access, made straightforward by MEV infrastructure on Solana.

### Recommendation
Make the slippage-protection parameters mandatory (non-`Option`) for both `Withdraw` and `Deposit` instructions, matching the pattern already used for `SwapBaseIn`/`SwapBaseOut`, so that every withdraw/deposit is required to specify and enforce a minimum acceptable amount, eliminating the possibility of silently skipping the check.

### Proof of Concept
1. Attacker observes a pending `Withdraw` transaction (with `min_coin_amount`/`min_pc_amount` = `None`) from victim in the mempool.
2. Attacker submits a large swap that shifts the coin/pc vault ratio unfavorably for the victim's withdraw direction.
3. Victim's `Withdraw` executes: since `min_coin_amount`/`min_pc_amount` are `None`, the check at `program/src/processor.rs:1780-1786` is bypassed, and the victim receives `coin_amount`/`pc_amount` computed from the post-swap, worse ratio via `InvariantPool::exchange_pool_to_token` (`program/src/processor.rs:1751-1761`), resulting in fewer tokens than the victim expected when signing at the pre-swap ratio.
4. The same sandwich pattern applies to `Deposit` when `other_amount_min` is `None` (`program/src/processor.rs:1223-1242`, `1274-1293`), causing the victim to deposit at a worse ratio and receive less LP than expected for their coin/pc contribution.

### Citations

**File:** program/src/instruction.rs (L56-75)
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

**File:** program/src/instruction.rs (L418-425)
```rust
            9 => {
                let (amount_in, rest) = Self::unpack_u64(rest)?;
                let (minimum_amount_out, _rest) = Self::unpack_u64(rest)?;
                Self::SwapBaseIn(SwapInstructionBaseIn {
                    amount_in,
                    minimum_amount_out,
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

**File:** program/src/processor.rs (L1779-1812)
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
            Invokers::token_burn(
                token_program_info.clone(),
                user_source_lp_info.clone(),
                amm_lp_mint_info.clone(),
                source_lp_owner_info.clone(),
                withdraw.amount,
            )?;
            amm.lp_amount = amm.lp_amount.checked_sub(withdraw.amount).unwrap();
```
