### Title
No support for Fee-on-Transfer tokens leads to swap/deposit accounting mismatch and pool insolvency - (File: `program/src/processor.rs`, `program/src/invokers.rs`)

### Summary
The AMM's `Deposit`, `SwapBaseIn`, and `SwapBaseOut` instruction handlers compute the amount transferred into and out of the coin/pc vaults using the caller-supplied nominal amount (`deduct_coin_amount`, `deduct_pc_amount`, `swap.amount_in`, `swap_in_after_add_fee`) and then call `Invokers::token_transfer`/`token_transfer_with_authority`, which simply issue an `spl_token::instruction::transfer` for that exact nominal amount without verifying the delta actually received by the destination account. If either the coin or pc mint is a fee-on-transfer (or rebasing) SPL token, the vault will receive less than the nominal amount used in the swap/LP math, while the program still pays out/mints based on the full nominal amount.

### Finding Description
For swaps, `process_swap_base_in`/`process_swap_base_in_v2`/`process_swap_base_out` compute `total_pc_without_take_pnl`/`total_coin_without_take_pnl` from the vault's on-chain balance (read via `Self::unpack_token_account`) *before* the current transaction's inbound transfer, then use `swap.amount_in` (the full nominal input) to derive `swap_amount_out`/`swap_in_after_add_fee` via `Calculator::swap_token_amount_base_in`. The program then executes:
<cite repo="AYontt/raydium-amm--021" path="program/src/processor.rs" start="2000-2022" end="2022" />
transferring `swap.amount_in` from the user into `amm_coin_vault_info` and paying out `swap_amount_out` from `amm_pc_vault_info` to the user, based on the assumption that the full `swap.amount_in` lands in the vault: [1](#0-0) 

The underlying transfer primitive does not check the destination's balance delta: [2](#0-1) 

The same pattern occurs for `Deposit`, where `deduct_coin_amount`/`deduct_pc_amount` (derived from the ratio of `max_coin_amount`/`max_pc_amount` to the pool's existing reserves) are transferred via `Invokers::token_transfer`, and `mint_lp_amount` is minted to the user based on those nominal amounts, not on what the vault actually received: [3](#0-2) 

If the coin or pc mint applies a transfer fee (fee-on-transfer) or is a rebasing token, the vault's actual received balance will be strictly less than the nominal amount used to (a) compute `swap_amount_out` for the counterparty leg of a swap, or (b) compute `mint_lp_amount` for a deposit. Because `total_coin_without_take_pnl`/`total_pc_without_take_pnl` and `target_orders.calc_pnl_x`/`calc_pnl_y` are subsequently derived from these nominal deduct/transfer amounts (see the `checked_add`/`checked_sub` updates using `deduct_coin_amount`/`deduct_pc_amount`), the AMM's internal reserve/pnl accounting becomes permanently inconsistent with the true on-chain vault balances.

### Impact Explanation
For swaps, an attacker can pick a fee-on-transfer coin/pc mint (or any mint the pool is configured with that later becomes fee-bearing, e.g., via mint extension) and repeatedly swap: the pool pays out the counter-asset computed off the full nominal input while only receiving the fee-adjusted (smaller) actual amount, which drains the AMM's real economic reserves faster than the constant-product invariant intends, causing insolvency of the pool relative to the liabilities it owes to remaining LPs. For deposits, `mint_lp_amount` is minted based on the nominal `deduct_coin_amount`/`deduct_pc_amount` even though the vault receives less, over-minting LP tokens relative to real backing and diluting/harming honest LPs on withdrawal — a permanent loss of LP-fund value. This is a concrete insolvent-pool-accounting / fund-loss issue reachable by any unprivileged swapper or LP through the standard `SwapBaseIn`/`SwapBaseOut`/`Deposit` instructions with attacker-chosen (or pool-creator-chosen) mints.

### Likelihood Explanation
Likelihood depends on a pool being created with a fee-on-transfer/rebasing token as `coin_mint` or `pc_mint`. The Raydium legacy AMM program does not restrict mints to the classic SPL Token program's fee-less semantics anywhere in `Initialize2`/`process_deposit`/`process_swap_base_in`, so nothing in the reachable instruction set prevents pairing the pool with such a token today or in the future if such tokens are onboarded. Given this is a known, previously flagged class of issue (per the referenced external report) and no explicit mitigation (balance-delta based accounting) exists in this codebase's transfer paths, the likelihood is realistic whenever such tokens are used with this AMM.

### Recommendation
For every inbound transfer into an AMM vault (`Deposit`, `SwapBaseIn`, `SwapBaseOut`), read the vault's token balance immediately before and after calling `Invokers::token_transfer`, and use the actual received delta (rather than the nominal instruction-supplied amount) for all subsequent invariant/reserve/pnl calculations (`mint_lp_amount`, `swap_amount_out`, `calc_pnl_x`/`calc_pnl_y` updates). Alternatively, explicitly reject pools/swaps whose coin or pc mint carries a transfer-fee extension or any fee-on-transfer behavior at `Initialize2` time.

### Proof of Concept
1. Pool creator initializes an AMM pool via `Initialize2` where the `pc_mint` is a fee-on-transfer SPL token (e.g., 1% transfer fee), and `coin_mint` is a normal token.
2. Attacker calls `SwapBaseIn` with `user_source_info` = their pc token account, sending `amount_in = X` pc tokens.
3. `process_swap_base_in` computes `swap_amount_out` (coin tokens to pay attacker) using the full `X` as input into `Calculator::swap_token_amount_base_in`, per `program/src/processor.rs:2024-2035` (`PC2Coin` branch).
4. `Invokers::token_transfer` moves `X` from attacker to `amm_pc_vault_info`, but due to the 1% fee, the vault's real balance only increases by `0.99 * X`.
5. The attacker receives `swap_amount_out` coin tokens computed as if `X` (not `0.99*X`) entered the pool — the pool now holds strictly less pc reserve than the invariant assumed, silently transferring value from remaining LPs to the attacker on every such swap, compounding pool insolvency over repeated calls.

### Citations

**File:** program/src/processor.rs (L1327-1350)
```rust
        Invokers::token_transfer(
            token_program_info.clone(),
            user_source_coin_info.clone(),
            amm_coin_vault_info.clone(),
            source_owner_info.clone(),
            deduct_coin_amount,
        )?;
        Invokers::token_transfer(
            token_program_info.clone(),
            user_source_pc_info.clone(),
            amm_pc_vault_info.clone(),
            source_owner_info.clone(),
            deduct_pc_amount,
        )?;
        Invokers::token_mint_to(
            token_program_info.clone(),
            amm_lp_mint_info.clone(),
            user_dest_lp_info.clone(),
            amm_authority_info.clone(),
            AUTHORITY_AMM,
            amm.nonce as u8,
            mint_lp_amount,
        )?;
        amm.lp_amount = amm.lp_amount.checked_add(mint_lp_amount).unwrap();
```

**File:** program/src/processor.rs (L2001-2023)
```rust
            SwapDirection::Coin2PC => {
                if swap_amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source coin to amm_coin_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_source_owner.clone(),
                    swap.amount_in,
                )?;
                // withdraw amm_pc_vault to destination pc
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap_amount_out,
                )?;
            }
```

**File:** program/src/invokers.rs (L147-168)
```rust
    /// Issue a spl_token `Transfer` instruction.
    pub fn token_transfer<'a>(
        token_program: AccountInfo<'a>,
        source: AccountInfo<'a>,
        destination: AccountInfo<'a>,
        owner: AccountInfo<'a>,
        deposit_amount: u64,
    ) -> Result<(), ProgramError> {
        let ix = spl_token::instruction::transfer(
            token_program.key,
            source.key,
            destination.key,
            owner.key,
            &[],
            deposit_amount,
        )?;
        solana_program::program::invoke_signed(
            &ix,
            &[source, destination, owner, token_program],
            &[],
        )
    }
```
