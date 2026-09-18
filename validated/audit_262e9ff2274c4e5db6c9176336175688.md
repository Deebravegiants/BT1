I have sufficient evidence now to finalize the analog.

### Title
Optional slippage parameters in `Withdraw` instruction allow sandwich attacks on LP withdrawals - (`program/src/processor.rs`)

### Summary
The `Withdraw` instruction's slippage protection fields, `min_coin_amount` and `min_pc_amount`, are declared as `Option<u64>` and are entirely skippable by the instruction data encoder/decoder. When a caller omits them (or a client library defaults to not including them, as suggested by the `slippage_limit: false` flag documented in the README), `process_withdraw` skips the slippage check entirely and transfers whatever `coin_amount`/`pc_amount` are computed from the AMM's live vault balances at execution time — exactly mirroring the Sherlock report's root cause where `minBuyAmount` defaults to `0` and bypasses the `MaxSlippageExceeded` check.

### Finding Description
`WithdrawInstruction` defines `min_coin_amount` and `min_pc_amount` as optional fields: [1](#0-0) 

During unpacking, if the instruction data is shorter than expected (i.e., the caller does not append the 16 extra bytes), both fields decode to `None` with no error: [2](#0-1) 

In `process_withdraw`, the pool computes `coin_amount`/`pc_amount` from the current (live, manipulable) vault balances via `Calculator::calc_total_without_take_pnl_no_orderbook` and the LP-to-token exchange rate, then only applies the slippage check `if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some()`. If either field is `None`, the check block is skipped entirely and the token transfers proceed unconditionally: [3](#0-2) 

This is structurally identical to the reported vulnerability class: a value that should enforce minimum-output slippage protection is instead optional/zero-equivalent, letting the transaction execute against manipulated pool reserves.

### Impact Explanation
An attacker monitoring the mempool for a `Withdraw` transaction that omits `min_coin_amount`/`min_pc_amount` can sandwich it: front-run with a swap that skews the coin/pc vault ratio, let the victim's withdraw execute at the skewed ratio (receiving far less of one asset and disproportionately more of the other, or simply less total value after the attacker's back-run swap restores the price and captures the spread), then back-run to restore price and pocket the difference. This directly steals value from the withdrawing LP, matching the High-severity impact in the original report (LP/user receives materially less than expected due to lack of enforced slippage control).

### Likelihood Explanation
Likelihood is high whenever a client omits the optional min amounts — which the program itself permits and which the bundled CLI/library exposes as a togglable `slippage_limit: false` option per the README example. Any transaction built without these fields is trivially detectable on-chain/in the mempool and sandwichable by any party running a bot, with attacker-controlled swap instructions in the same block/transaction sequence — no privileged access required.

### Recommendation
Make `min_coin_amount` and `min_pc_amount` mandatory (non-optional `u64`) fields in `WithdrawInstruction`, removing the `Option` and the associated `is_some()` gating in `process_withdraw`, so the slippage check in [4](#0-3)  is always enforced. Alternatively, if backward compatibility must be preserved, reject `None` values for withdrawals above a nonzero threshold, or require the caller to explicitly pass `0` (making the omission of protection an explicit, auditable client choice rather than a silent default).

### Proof of Concept
1. Pool has coin/pc reserves R_coin, R_pc; attacker observes a pending `Withdraw(amount, min_coin_amount=None, min_pc_amount=None)` transaction from a victim in the mempool.
2. Attacker front-runs with `SwapBaseIn`/`SwapBaseOut` that shifts the coin/pc ratio unfavorably for the victim's proportional withdrawal (e.g., dumping pc into the pool to depress the coin price).
3. Victim's `Withdraw` executes: since `withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some()` evaluates false, the code at [5](#0-4)  skips the slippage check, and `coin_amount`/`pc_amount` (computed from the now-skewed reserves) are transferred to the victim regardless of how unfavorable the ratio is.
4. Attacker back-runs to revert the swap, restoring the price and capturing the spread extracted from the victim's withdrawal, at no risk since both legs execute atomically around the victim's transaction.

### Citations

**File:** program/src/instruction.rs (L67-75)
```rust
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

**File:** program/src/processor.rs (L1779-1816)
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
        } else {
            // calc error
            return Err(AmmError::TakePnlError.into());
        }
```
