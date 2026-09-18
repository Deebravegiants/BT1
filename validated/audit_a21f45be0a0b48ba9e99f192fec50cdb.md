### Title
Missing Freeze-Authority Validation on `coin_mint`/`pc_mint` Allows Permanent Freezing of Pool Vaults - ([File: program/src/processor.rs])

### Summary
`process_initialize2` validates that the LP mint has no freeze authority, but never checks whether the pool's `coin_mint` or `pc_mint` (the actual tradable assets held in `coin_vault`/`pc_vault`) have a freeze authority. If either mint has an active freeze authority, that authority can freeze the pool's `coin_vault` or `pc_vault` token account at any time post-initialization, permanently blocking `Deposit`, `Withdraw`, `SwapBaseIn`/`SwapBaseOut` (and V2 variants) and `WithdrawPnl`, locking all LP and swap funds in the pool.

### Finding Description
During pool creation, `process_initialize2` unpacks and validates `amm_coin_vault` and `amm_pc_vault` (owner, non-zero balance, no delegate, no close authority) and separately checks that the LP mint has no freeze authority: [1](#0-0) 

However, there is no equivalent check on `amm_coin_mint_info` or `amm_pc_mint_info` — the mints backing the vaults that hold all pooled liquidity. A grep across the codebase confirms `freeze_authority` is referenced exactly once, only for the LP mint, and never for the coin/pc mints used in swaps, deposits and withdrawals.

Since these coin/pc vaults are the exact accounts used by every subsequent operation:
- `process_deposit` transfers into `amm_coin_vault`/`amm_pc_vault`.
- `process_withdraw` / `process_withdrawpnl` transfer out of them.
- `process_swap_base_in`/`process_swap_base_out` (and V2 variants) both deposit into and withdraw from them via `Invokers::token_transfer` / `Invokers::token_transfer_with_authority`, e.g.: [2](#0-1) 

If the freeze authority of `coin_mint` or `pc_mint` freezes the corresponding pool vault account (a normal SPL Token operation available to any mint's freeze authority, requiring no cooperation from the pool), every one of these instructions will fail at the SPL Token CPI level because frozen token accounts cannot be debited or credited. There is no unfreeze path controlled by the pool program, so the freeze is permanent from the protocol's perspective (only the mint's freeze authority — an entity entirely outside pool control — could reverse it).

### Impact Explanation
This causes a permanent Denial of Service on the pool and, because LP shares cannot be redeemed once the corresponding vault is frozen, permanent loss of access to all coin/pc funds and LP funds locked in that pool. This meets the Medium/High bar: unbacked freezing of user/LP funds reachable by any pool creator picking a malicious/mutable mint during `Initialize2`, with no privileged action required afterward beyond the external mint authority's own freeze call.

### Likelihood Explanation
Likelihood is Medium: it requires a pool to be created with a coin or pc mint that retains a freeze authority (common for many SPL tokens, including some with legitimate compliance-related freeze authorities that could later be compromised or misused). Since `Initialize2` performs no validation preventing this, any pool creator (potentially unaware) or malicious token issuer can set up a pool with such a mint, and the freeze authority can trigger the DoS at will post hoc.

### Recommendation
In `process_initialize2`, after unpacking `amm_coin_mint_info`/`amm_pc_mint_info` (or the vault mints), explicitly reject mints that have a freeze authority set, mirroring the existing LP mint check:
```rust
let coin_mint = Self::unpack_mint(&amm_coin_mint_info, spl_token_program_id)?;
if coin_mint.freeze_authority.is_some() {
    return Err(AmmError::InvalidFreezeAuthority.into());
}
let pc_mint = Self::unpack_mint(&amm_pc_mint_info, spl_token_program_id)?;
if pc_mint.freeze_authority.is_some() {
    return Err(AmmError::InvalidFreezeAuthority.into());
}
```
placed alongside the existing checks at [3](#0-2) .

### Proof of Concept
1. Attacker/pool-creator mints a new SPL token `X` with a freeze authority they control (or use any existing SPL token that already has an active freeze authority).
2. Attacker calls `Initialize2` to create a Raydium AMM pool with `coin_mint = X`, `pc_mint = <any token>`. Initialization succeeds because no freeze-authority check is performed on `X` (only the LP mint is checked, at [4](#0-3) ).
3. Liquidity providers deposit into the pool via `Deposit`, and traders swap through `SwapBaseIn`/`SwapBaseOut`, growing `amm_coin_vault`'s balance.
4. The freeze authority of `X` calls the SPL Token `FreezeAccount` instruction on `amm_coin_vault`.
5. All subsequent `Deposit`, `Withdraw`, `WithdrawPnl`, and swap instructions touching `amm_coin_vault` (e.g., the transfer calls at [5](#0-4) ) now fail at the SPL Token CPI layer, permanently trapping all coin-side and LP funds in the pool.

### Citations

**File:** program/src/processor.rs (L850-895)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        check_assert_eq!(
            amm_coin_vault.owner,
            *amm_authority_info.key,
            "coin_vault_owner",
            AmmError::InvalidOwner
        );
        if amm_coin_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_coin_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
        }
        if amm_coin_vault.close_authority.is_some() {
            return Err(AmmError::InvalidCloseAuthority.into());
        }
        check_assert_eq!(
            *amm_coin_mint_info.key,
            amm_coin_vault.mint,
            "coin_mint",
            AmmError::InvalidCoinMint
        );
        // unpack and check token_pc
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        check_assert_eq!(
            amm_pc_vault.owner,
            *amm_authority_info.key,
            "pc_vault_owner",
            AmmError::InvalidOwner
        );
        if amm_pc_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_pc_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
        }
        if amm_pc_vault.close_authority.is_some() {
            return Err(AmmError::InvalidCloseAuthority.into());
        }
        check_assert_eq!(
            *amm_pc_mint_info.key,
            amm_pc_vault.mint,
            "pc_mint",
            AmmError::InvalidPCMint
        );
```

**File:** program/src/processor.rs (L897-906)
```rust
        let lp_mint = Self::unpack_mint(&amm_lp_mint_info, spl_token_program_id)?;
        if lp_mint.supply != 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if COption::Some(*amm_authority_info.key) != lp_mint.mint_authority {
            return Err(AmmError::InvalidOwner.into());
        }
        if lp_mint.freeze_authority.is_some() {
            return Err(AmmError::InvalidFreezeAuthority.into());
        }
```

**File:** program/src/processor.rs (L2005-2022)
```rust
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
```
