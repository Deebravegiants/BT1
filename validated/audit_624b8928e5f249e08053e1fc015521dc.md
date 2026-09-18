### Title
`calc_total_without_take_pnl_no_orderbook()` can revert on underflow and DoS all swap/deposit/withdraw operations - (File: `program/src/math.rs`)

### Summary
`Calculator::calc_total_without_take_pnl_no_orderbook()` unconditionally subtracts the pool's accrued-but-unwithdrawn PnL (`amm.state_data.need_take_pnl_pc` / `need_take_pnl_coin`) from the live vault token balances, propagating a hard error via `checked_sub` when the subtrahend exceeds the vault balance. This function gates every core user-facing instruction (deposit, withdraw, both swap directions, and `withdrawpnl`), so any state where `need_take_pnl_pc/coin` drifts above the actual vault balance freezes the whole pool.

### Finding Description [1](#0-0) 

```rust
pub fn calc_total_without_take_pnl_no_orderbook<'a>(
    pc_amount: u64,
    coin_amount: u64,
    amm: &'a AmmInfo,
) -> Result<(u64, u64), AmmError> {
    let total_pc_without_take_pnl = pc_amount
        .checked_sub(amm.state_data.need_take_pnl_pc)
        .ok_or(AmmError::CheckedSubOverflow)?;
    let total_coin_without_take_pnl = coin_amount
        .checked_sub(amm.state_data.need_take_pnl_coin)
        .ok_or(AmmError::CheckedSubOverflow)?;
    Ok((total_pc_without_take_pnl, total_coin_without_take_pnl))
}
```

This is the exact structural analog of the reported `totalUnderlyingMinusSponsored()` bug: a bookkeeping value that only ever grows (`need_take_pnl_pc`/`need_take_pnl_coin`, incremented every time `calc_take_pnl()` is invoked, see [2](#0-1) ) is subtracted from a live external balance (`amm_pc_vault.amount` / `amm_coin_vault.amount`) with no floor/clamp, and the result is depended upon by essentially every instruction that touches the pool:

- `process_deposit` [3](#0-2) 
- `process_withdraw` [4](#0-3) 
- `process_swap_base_in` / `process_swap_base_in_v2` [5](#0-4) 
- `process_swap_base_out` (v1/v2) [6](#0-5) 
- `process_withdrawpnl` itself [7](#0-6) 

`need_take_pnl_pc`/`need_take_pnl_coin` represent PnL that has been mathematically carved out of the pool's reserves by `calc_take_pnl()` but has not yet physically left the vault (it is only zeroed out when the privileged `pnl_owner` calls `withdrawpnl`, see [8](#0-7) ). Under correct, self-consistent bookkeeping the vault balance should always be `>= need_take_pnl_*`, but the invariant is only maintained by careful arithmetic across many code paths and rounding operations (`restore_decimal`, `normalize_decimal_v2`, integer-sqrt-based `calc_take_pnl`, and floor/ceil rounding in `InvariantPool`/`InvariantToken` exchange functions). Any accumulated rounding drift, or a delay in calling `withdrawpnl` while ordinary swap/withdraw activity continues to compress the vault relative to the accrued (but not-yet-transferred) PnL entitlement, causes `pc_amount.checked_sub(amm.state_data.need_take_pnl_pc)` (or the coin equivalent) to underflow, returning `AmmError::CheckedSubOverflow` and reverting the transaction — exactly the failure mode described in the referenced report, just manifesting as an explicit `Err` instead of an unguarded Solidity underflow revert.

### Impact Explanation
Because `calc_total_without_take_pnl_no_orderbook()` is called at the top of `deposit`, `withdraw`, and all four swap instructions, a single stuck state (vault balance dipping at or below the accrued `need_take_pnl_pc`/`need_take_pnl_coin`) freezes deposits, withdrawals, and swaps for the entire pool simultaneously. This is a pool-wide denial of service that blocks LPs from withdrawing their funds and blocks all trading, until the `pnl_owner` intervenes via `withdrawpnl` (a step the function itself may also not reach cleanly if the underflow condition persists across the check at line 1505-1506 comparing `need_take_pnl_coin <= amm_coin_vault.amount`). This matches the "permanent freezing of user or LP funds" acceptance criterion.

### Likelihood Explanation
The condition is reachable purely through normal, unprivileged usage: swappers trigger `calc_take_pnl()` on every swap and deposit/withdraw call, continuously increasing `need_take_pnl_pc/coin`, while LPs can withdraw large portions of the pool's reserves via `process_withdraw`, shrinking the vault balance that the PnL entitlement is subtracted from. No malicious signer, admin key, or non-default build is required — only ordinary trading activity plus the operational reality that `withdrawpnl` is called intermittently by the `pnl_owner`, not on every transaction.

### Recommendation
Mirror the report's recommendation: clamp the subtraction instead of failing/underflowing, e.g. return `0` for a side when `need_take_pnl_* > vault_amount`, and additionally audit `calc_take_pnl()`'s rounding paths to ensure `need_take_pnl_pc/coin` can never legitimately exceed the real vault balance (e.g., by re-deriving them from live vault balances after each pool-composition-changing instruction rather than accumulating a monotonic entitlement counter independent of vault movements).

### Proof of Concept
1. Pool trades actively; each swap invokes `calc_take_pnl()`, incrementing `amm.state_data.need_take_pnl_pc`/`need_take_pnl_coin` per [9](#0-8) , while the `pnl_owner` does not call `withdrawpnl`.
2. LPs call `process_withdraw` repeatedly, removing coin/pc from the vaults proportional to LP tokens burned [10](#0-9) , shrinking `amm_pc_vault.amount`/`amm_coin_vault.amount` while `need_take_pnl_pc/coin` remains unchanged (only zeroed by `withdrawpnl`).
3. Once accumulated rounding/timing pushes `need_take_pnl_pc` (or `_coin`) at or above the live vault balance, the next call to any of `deposit`, `withdraw`, `swap_base_in(_v2)`, or `swap_base_out(_v2)` invokes `calc_total_without_take_pnl_no_orderbook()` [11](#0-10)  which returns `AmmError::CheckedSubOverflow`, reverting the transaction and freezing the pool for all users until an admin withdraws the pending PnL.

### Citations

**File:** program/src/math.rs (L238-250)
```rust
    pub fn calc_total_without_take_pnl_no_orderbook<'a>(
        pc_amount: u64,
        coin_amount: u64,
        amm: &'a AmmInfo,
    ) -> Result<(u64, u64), AmmError> {
        let total_pc_without_take_pnl = pc_amount
            .checked_sub(amm.state_data.need_take_pnl_pc)
            .ok_or(AmmError::CheckedSubOverflow)?;
        let total_coin_without_take_pnl = coin_amount
            .checked_sub(amm.state_data.need_take_pnl_coin)
            .ok_or(AmmError::CheckedSubOverflow)?;
        Ok((total_pc_without_take_pnl, total_coin_without_take_pnl))
    }
```

**File:** program/src/processor.rs (L244-262)
```rust
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

**File:** program/src/processor.rs (L1148-1153)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1458-1464)
```rust
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1505-1529)
```rust
        if amm.state_data.need_take_pnl_coin <= amm_coin_vault.amount
            && amm.state_data.need_take_pnl_pc <= amm_pc_vault.amount
        {
            // coin & pc is enough, transfer directly
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_coin_vault_info.clone(),
                user_pnl_coin_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                amm.state_data.need_take_pnl_coin,
            )?;
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_pc_vault_info.clone(),
                user_pnl_pc_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                amm.state_data.need_take_pnl_pc,
            )?;
            // clear need take pnl
            amm.state_data.need_take_pnl_coin = 0u64;
            amm.state_data.need_take_pnl_pc = 0u64;
```

**File:** program/src/processor.rs (L1719-1724)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
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

**File:** program/src/processor.rs (L2154-2159)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L2342-2347)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```
