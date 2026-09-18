### Title
Withdraw slippage guard is skipped entirely when only one of `min_coin_amount`/`min_pc_amount` is set, allowing sandwich attacks that drain LP funds - ([File: program/src/processor.rs])

### Summary
The PostCSS advisory's bug class is: a security guard that is supposed to always validate attacker-influenced data instead only runs when an unrelated/optional value happens to be present (`if (cssFile) { ...traversal checks... }`), so when that value is absent the guard is silently skipped and the check that should have blocked the exploit never runs. The same "guard only fires when *all* of a set of optional fields are populated" pattern exists in `process_withdraw`'s slippage protection for the `Withdraw` instruction.

### Finding Description
`WithdrawInstruction` carries slippage protection as two independent `Option<u64>` fields, `min_coin_amount` and `min_pc_amount` [1](#0-0) . In `process_withdraw`, after computing `coin_amount`/`pc_amount` from the pool's current on-chain ratio, the enforcement of the minimum-output guard is gated by a logical AND over both `Option`s being `Some`:

```rust
if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some() {
    if withdraw.min_coin_amount.unwrap() > coin_amount
        || withdraw.min_pc_amount.unwrap() > pc_amount
    {
        return Err(AmmError::ExceededSlippage.into());
    }
}
``` [2](#0-1) 

If either field is `None` — which is entirely attacker/caller-controlled instruction data submitted in the single withdraw transaction — the whole slippage check block is skipped, and the withdrawal proceeds unconditionally at whatever `coin_amount`/`pc_amount` the pool state yields at execution time [3](#0-2) . This is structurally identical to the PostCSS defect: a protective check exists in the code, but is nested behind a condition on an optional value's presence rather than being unconditionally applied, so omitting that optional value bypasses the protection completely rather than falling back to a safe default (e.g., "no slippage tolerance means reject" or "treat missing bound as maximally strict").

Because Solana transactions are atomic but not exclusive with respect to prior/following transactions in the same slot, an adversary (a searcher/validator or anyone able to submit surrounding transactions) can sandwich a withdraw call that has one of the two min-amount fields unset: front-run with a large swap that skews the coin/pc ratio, let the victim's `process_withdraw` execute and burn LP at the manipulated ratio (receiving far less of the token whose minimum wasn't checked), then back-run to restore the ratio and capture the difference.

### Impact Explanation
A successful sandwich against an under-specified `Withdraw` instruction directly reduces the value a liquidity provider receives for burning their LP tokens, which is a concrete transfer of value from the LP to the attacker completed within reachable, unprivileged instructions (`SwapBaseIn`/`SwapBaseOut` before and after `Withdraw`) — matching the "concrete theft of LP funds" bar. The vault balances and LP burn accounting (`amm.lp_amount`, `target_orders.calc_pnl_*`) remain internally consistent, so this is not a protocol insolvency, but it is a real economic loss enabled purely by a validation-skip bug in the on-chain instruction handler, not client behavior.

### Likelihood Explanation
Exploitability depends entirely on whether callers (wallets, aggregators, or scripts) submit a `Withdraw` instruction leaving one of `min_coin_amount`/`min_pc_amount` as `None` — this is legal, un-flagged instruction data that the program happily accepts and processes with zero protection. Any pool with meaningful trading volume is a viable sandwich target whenever such a transaction appears in the mempool/leader schedule.

### Recommendation
Change the guard so slippage is enforced independently and unconditionally per field (reject if `min_coin_amount` is `Some` and violated, and separately reject if `min_pc_amount` is `Some` and violated), or better, require both fields to be `Some` in `process_withdraw` (reject with `AmmError::InvalidInput` if either is `None`) so the protection can never be silently bypassed by omitting only one of the two options.

### Proof of Concept
1. Attacker observes a pending `Withdraw` transaction (via mempool/leader visibility) where the instruction data encodes `min_coin_amount = Some(x)` but `min_pc_amount = None` (or vice versa) — a value permitted and accepted by `AmmInstruction::Withdraw` unpacking with no rejection in `process_withdraw`.
2. Attacker submits a `SwapBaseIn`/`SwapBaseOut` transaction immediately before the victim's transaction to skew the pool's pc/coin ratio in `amm_pc_vault`/`amm_coin_vault`.
3. The victim's `Withdraw` executes: because `min_pc_amount.is_some()` is `false`, the entire `if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some() { ... }` block in `program/src/processor.rs` lines 1780-1786 is skipped, so no slippage check runs at all, and the victim's LP is burned and `pc_amount`/`coin_amount` transferred at the manipulated ratio.
4. Attacker submits a reverse swap to restore the ratio, netting the difference extracted from the victim's withdrawal at the LP's expense. [4](#0-3)

### Citations

**File:** program/src/instruction.rs (L813-816)
```rust
    amount: u64,
    min_coin_amount: Option<u64>,
    min_pc_amount: Option<u64>,
) -> Result<Instruction, ProgramError> {
```

**File:** program/src/processor.rs (L1751-1817)
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

        encode_ray_log(WithdrawLog {
            log_type: LogType::Withdraw.into_u8(),
            withdraw_lp: withdraw.amount,
            user_lp: user_source_lp.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            pool_lp: amm.lp_amount,
            calc_pnl_x: target_orders.calc_pnl_x,
            calc_pnl_y: target_orders.calc_pnl_y,
            out_coin: coin_amount,
            out_pc: pc_amount,
        });
        if withdraw.amount == 0 || coin_amount == 0 || pc_amount == 0 {
            return Err(AmmError::InvalidInput.into());
        }

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
