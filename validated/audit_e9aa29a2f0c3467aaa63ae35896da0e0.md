### Title
Missing `coin_vault_mint == pc_vault_mint` guard in `process_withdraw()` — ([File: program/src/processor.rs])

### Summary
Every liquidity-mutating and swap entrypoint in the AMM processor — `process_deposit`, `process_swap_base_in`, `process_swap_base_out`, `process_swap_base_in_v2`, and `process_swap_base_out_v2` — explicitly rejects operating on a pool whose `coin_vault_mint` equals its `pc_vault_mint` via the check `if amm.pc_vault_mint == amm.coin_vault_mint { return Err(AmmError::NotAllowed.into()); }`. `process_withdraw()`, which performs the analogous liquidity-removal logic against the same `AmmInfo` state, does not contain this check at all.

### Finding Description
The guard against a degenerate pool where both vaults share the same mint is present at the top of: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

`process_withdraw()`, which loads the same `AmmInfo` account and computes pool totals/PnL/LP burn amounts using the same `coin_vault_mint`/`pc_vault_mint` fields, has no equivalent check anywhere in its body: [6](#0-5) [7](#0-6) 

This is directly analogous to the reported bug class: a guard was added to a set of sibling functions performing the same class of operation on the same shared state, but one function performing equivalent logic (`process_withdraw` vs. `process_deposit`/swap variants) was left without the check, allowing the state guarded against elsewhere to still be reached and acted upon through the omitted path.

### Impact Explanation
If an `AmmInfo` account can ever end up with `coin_vault_mint == pc_vault_mint` (e.g., through legacy/degenerate pools, a future code path, or any state where this invariant is violated), `process_deposit` and all swap instructions would refuse to operate on it, but `process_withdraw` would still execute: computing `total_pc_without_take_pnl`/`total_coin_without_take_pnl` via `Calculator::calc_total_without_take_pnl_no_orderbook`, taking PnL, and transferring both `coin_amount` and `pc_amount` out of what are effectively the same underlying token vault/mint, then burning LP. This breaks the assumption (relied upon elsewhere in the codebase) that the two vaults are always distinct assets, and can lead to double-counting/over-withdrawal of a single underlying asset relative to LP share, resulting in insolvent pool accounting or loss of funds for remaining LPs.

### Likelihood Explanation
This requires an `AmmInfo` in the degenerate `coin_vault_mint == pc_vault_mint` state to exist. Whether `process_initialize2` can produce or a state transition can lead to such a pool could not be fully confirmed within the available index (the full body of `process_initialize2` and any mint-inequality validation there was not retrievable in this pass). Given that the developers found it necessary to add this exact check to five other instruction handlers, the omission in `process_withdraw` is best characterized as an inconsistency that removes defense-in-depth for a state the rest of the program explicitly treats as invalid.

### Recommendation
Add the same guard to `process_withdraw()` immediately after loading `amm`, mirroring `process_deposit`:
```rust
let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
if amm.pc_vault_mint == amm.coin_vault_mint {
    return Err(AmmError::NotAllowed.into());
}
``` [8](#0-7) 

### Proof of Concept
Not independently reproducible from the index alone: constructing an on-chain `AmmInfo` with `coin_vault_mint == pc_vault_mint` requires confirming whether `process_initialize2` enforces mint inequality at pool creation, which was not fully retrievable within the tool budget. The finding rests on the confirmed source-level inconsistency: the identical `NotAllowed` guard exists in `process_deposit`/`process_swap_base_in`/`process_swap_base_out`/`process_swap_base_in_v2`/`process_swap_base_out_v2` but is absent from `process_withdraw`, matching the report's bug class of a check applied to sibling functions but omitted from one analogous code path.

### Citations

**File:** program/src/processor.rs (L1076-1079)
```rust
        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        if amm.pc_vault_mint == amm.coin_vault_mint {
            return Err(AmmError::NotAllowed.into());
        }
```

**File:** program/src/processor.rs (L1543-1651)
```rust
    pub fn process_withdraw(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        withdraw: WithdrawInstruction,
    ) -> ProgramResult {
        let input_account_len = accounts.len();
        let (
            token_program_info,
            amm_info,
            amm_authority_info,
            amm_target_orders_info,
            amm_lp_mint_info,
            amm_coin_vault_info,
            amm_pc_vault_info,
            user_source_lp_info,
            user_dest_coin_info,
            user_dest_pc_info,
            source_lp_owner_info,
        ) = if input_account_len == 11 {
            // Recommended use due to openbook has not supported.
            let account_info_iter = &mut accounts.iter();
            let token_program_info = next_account_info(account_info_iter)?;

            let amm_info = next_account_info(account_info_iter)?;
            let amm_authority_info = next_account_info(account_info_iter)?;
            let amm_target_orders_info = next_account_info(account_info_iter)?;
            let amm_lp_mint_info = next_account_info(account_info_iter)?;
            let amm_coin_vault_info = next_account_info(account_info_iter)?;
            let amm_pc_vault_info = next_account_info(account_info_iter)?;

            let user_source_lp_info = next_account_info(account_info_iter)?;
            let user_dest_coin_info = next_account_info(account_info_iter)?;
            let user_dest_pc_info = next_account_info(account_info_iter)?;
            let source_lp_owner_info = next_account_info(account_info_iter)?;

            (
                token_program_info,
                amm_info,
                amm_authority_info,
                amm_target_orders_info,
                amm_lp_mint_info,
                amm_coin_vault_info,
                amm_pc_vault_info,
                user_source_lp_info,
                user_dest_coin_info,
                user_dest_pc_info,
                source_lp_owner_info,
            )
        } else {
            const ACCOUNT_LEN: usize = 20;
            if input_account_len != ACCOUNT_LEN
                && input_account_len != ACCOUNT_LEN + 1
                && input_account_len != ACCOUNT_LEN + 2
                && input_account_len != ACCOUNT_LEN + 3
            {
                return Err(AmmError::WrongAccountsNumber.into());
            }
            let account_info_iter = &mut accounts.iter();
            let token_program_info = next_account_info(account_info_iter)?;

            let amm_info = next_account_info(account_info_iter)?;
            let amm_authority_info = next_account_info(account_info_iter)?;
            let _amm_open_orders_info = next_account_info(account_info_iter)?;
            let amm_target_orders_info = next_account_info(account_info_iter)?;
            let amm_lp_mint_info = next_account_info(account_info_iter)?;
            let amm_coin_vault_info = next_account_info(account_info_iter)?;
            let amm_pc_vault_info = next_account_info(account_info_iter)?;
            if input_account_len == ACCOUNT_LEN + 2 || input_account_len == ACCOUNT_LEN + 3 {
                let _padding_account_info1 = next_account_info(account_info_iter)?;
                let _padding_account_info2 = next_account_info(account_info_iter)?;
            }

            let _market_program_info = next_account_info(account_info_iter)?;
            let _market_info = next_account_info(account_info_iter)?;
            let _market_coin_vault_info = next_account_info(account_info_iter)?;
            let _market_pc_vault_info = next_account_info(account_info_iter)?;
            let _market_vault_signer = next_account_info(account_info_iter)?;

            let user_source_lp_info = next_account_info(account_info_iter)?;
            let user_dest_coin_info = next_account_info(account_info_iter)?;
            let user_dest_pc_info = next_account_info(account_info_iter)?;
            let source_lp_owner_info = next_account_info(account_info_iter)?;

            let _market_event_q_info = next_account_info(account_info_iter)?;
            let _market_bids_info = next_account_info(account_info_iter)?;
            let _market_asks_info = next_account_info(account_info_iter)?;

            (
                token_program_info,
                amm_info,
                amm_authority_info,
                amm_target_orders_info,
                amm_lp_mint_info,
                amm_coin_vault_info,
                amm_pc_vault_info,
                user_source_lp_info,
                user_dest_coin_info,
                user_dest_pc_info,
                source_lp_owner_info,
            )
        };

        if !source_lp_owner_info.is_signer {
            return Err(AmmError::InvalidSignAccount.into());
        }
        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;

```

**File:** program/src/processor.rs (L1719-1762)
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

**File:** program/src/processor.rs (L1867-1870)
```rust
        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        if amm.pc_vault_mint == amm.coin_vault_mint {
            return Err(AmmError::NotAllowed.into());
        }
```

**File:** program/src/processor.rs (L2077-2080)
```rust
        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        if amm.pc_vault_mint == amm.coin_vault_mint {
            return Err(AmmError::NotAllowed.into());
        }
```

**File:** program/src/processor.rs (L2277-2280)
```rust
        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        if amm.pc_vault_mint == amm.coin_vault_mint {
            return Err(AmmError::NotAllowed.into());
        }
```

**File:** program/src/processor.rs (L2466-2469)
```rust
        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        if amm.pc_vault_mint == amm.coin_vault_mint {
            return Err(AmmError::NotAllowed.into());
        }
```
