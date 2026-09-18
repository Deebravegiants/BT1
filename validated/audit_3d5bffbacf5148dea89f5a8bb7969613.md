### Title
Withdraw slippage check bypassed when either `min_coin_amount` or `min_pc_amount` is `None` - (File: `program/src/processor.rs`)

### Summary
The `process_withdraw` function in `program/src/processor.rs` only enforces the caller-supplied minimum-output slippage check when **both** `min_coin_amount` and `min_pc_amount` are `Some`. Since these are `Option<u64>` fields fully controlled by the attacker-signed transaction's instruction data, a withdrawer (or an attacker crafting a malicious withdraw for a victim's LP position they control) can simply omit either field to withdraw with zero slippage protection, exposing the withdrawal to the exact sandwich/frontrun scenario described in the referenced HydraDX finding.

### Finding Description
`WithdrawInstruction` defines both minimum-output parameters as optional: [1](#0-0) 

In `process_withdraw`, the computed `coin_amount`/`pc_amount` a user will receive are checked against these minimums only if **both** are populated: [2](#0-1) 

```rust
if coin_amount < amm_coin_vault.amount && pc_amount < amm_pc_vault.amount {
    if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some() {
        if withdraw.min_coin_amount.unwrap() > coin_amount
            || withdraw.min_pc_amount.unwrap() > pc_amount
        {
            return Err(AmmError::ExceededSlippage.into());
        }
    }
    ...
}
```

Because the guard uses `&&` on `is_some()`, if either field is `None` (which is the fully attacker-controlled instruction payload for a single transaction), the entire slippage check is skipped — not just the check for the missing field. This is functionally equivalent to the HydraDX report's "no slippage check in `remove_liquidity`" bug class, but arguably worse: the on-chain code path *has* a mechanism for a slippage check, yet it can be trivially disabled from a single unprivileged, attacker-crafted transaction just by setting one optional field to `None`, allowing 100% unbounded slippage rather than a capped 2%.

An attacker who can observe a pending withdraw transaction (or who controls a bot submitting withdrawals, e.g., via a compromised/naive front-end that omits one of the two optional fields) can sandwich the withdrawal: push the pool's coin/pc ratio in a way that reduces the value of tokens returned to the withdrawer via `Invokers::token_transfer_with_authority` calls, then reverse the trade after, extracting the difference as MEV — with no on-chain protection at all.

### Impact Explanation
This allows unbounded slippage loss for a liquidity provider withdrawing funds, whenever the withdraw instruction supplies `None` for either `min_coin_amount` or `min_pc_amount` — this is not a hypothetical or invalid input; any client/integrator that doesn't set *both* fields (e.g. sets only one, intending partial protection) unintentionally disables protection entirely. Given the Amm pool logic transfers real `coin_amount`/`pc_amount` from `amm_coin_vault`/`amm_pc_vault` to the user based on state that can be manipulated by an attacker's prior/following swap transaction in the same block, this is a direct value-extraction path against LP funds, matching the accepted medium-severity classification of the referenced report.

### Likelihood Explanation
Reachable by any unprivileged party performing withdrawals (the LP owner signs, but the instruction data — including the `Option<u64>` minimums — is attacker/integrator controlled at construction time), and exploitable by any third party who can front-run/sandwich the withdrawal transaction in the same slot, exactly as demonstrated in the original report's POC methodology. No special privileges, leaked keys, or non-default builds are required — only a withdraw instruction lacking one of the two minimums (a very plausible/common integration pattern, since the two fields are independently `Option`al rather than an atomic pair).

### Recommendation
Change the guard so that supplying only one of the two minimums still enforces that one:
```rust
if let Some(min_coin) = withdraw.min_coin_amount {
    if min_coin > coin_amount {
        return Err(AmmError::ExceededSlippage.into());
    }
}
if let Some(min_pc) = withdraw.min_pc_amount {
    if min_pc > pc_amount {
        return Err(AmmError::ExceededSlippage.into());
    }
}
```
Additionally, consider requiring at least one of the two to be set, or exposing an aggregate minimum threshold (e.g., minimum LP-share redemption value), so that withdrawals cannot bypass slippage protection entirely by omission.

### Proof of Concept
1. Attacker/LP submits `Withdraw { amount, min_coin_amount: None, min_pc_amount: Some(x) }` (or vice versa, or both `None`) via the `withdraw()` instruction builder: [3](#0-2) 
2. In the same block/slot, a third party executes a swap (`process_swap_base_in`/`process_swap_base_out`) against the same pool to shift `amm_coin_vault`/`amm_pc_vault` balances, analogous to LP3's frontrunning swap in the HydraDX POC.
3. `process_withdraw` computes `coin_amount`/`pc_amount` from the now-skewed vault balances via `Calculator::calc_total_without_take_pnl_no_orderbook` and `InvariantPool::exchange_pool_to_token`: [4](#0-3) 
4. Because `withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some()` evaluates to `false`, the slippage check block is entirely skipped, and the transfer/burn proceeds with the unfavorable amounts: [5](#0-4) 
5. The attacker reverses their swap afterward, capturing the value difference extracted from the withdrawer with no on-chain limit.

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

**File:** program/src/instruction.rs (L813-822)
```rust
    amount: u64,
    min_coin_amount: Option<u64>,
    min_pc_amount: Option<u64>,
) -> Result<Instruction, ProgramError> {
    let data = AmmInstruction::Withdraw(WithdrawInstruction {
        amount,
        min_coin_amount,
        min_pc_amount,
    })
    .pack()?;
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
