### Title
Pool creator can permanently freeze all LP/user funds by using a malicious mint with a freeze authority as coin/pc mint - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` validates that the `lp_mint` created by the program has no `freeze_authority`, but it never validates that the attacker-supplied `amm_coin_mint_info` / `amm_pc_mint_info` mints have no `freeze_authority`. Since `Initialize2` is permissionless (any unprivileged user can create a pool), an attacker can supply a mint they control with a live `freeze_authority`, pair it with a legitimate token, seed the pool, and later freeze the resulting vault token account. This is the same root-cause pattern as the reported "unsound collateral design" bug: an attacker-chosen mint/freeze authority is accepted without validation, letting the attacker permanently freeze a token account that legitimate users depend on.

### Finding Description
In `process_initialize2` (`program/src/processor.rs`), the coin and pc mints are unpacked and only checked for basic sanity (different mints, non-zero vault balance, no delegate, no close authority on the *vault*, correct mint match), but there is no check on `coin_mint.freeze_authority` / `pc_mint.freeze_authority`: [1](#0-0) 

Compare this to the explicit protection that *is* applied to the LP mint just a few lines later: [2](#0-1) 

This asymmetry means the program author was clearly aware that an active freeze authority is dangerous (hence the `InvalidFreezeAuthority` check on `lp_mint`), but the same guard was never applied to `amm_coin_mint_info`/`amm_pc_mint_info`, even though `Initialize2` accepts these mints from an arbitrary, unprivileged caller and creates program-owned vault token accounts for them via `generate_amm_associated_spl_token`: [3](#0-2) 

Because a mint's `freeze_authority` gives its holder the unilateral, on-chain right to freeze *any* token account of that mint (including the pool's vault PDA), an attacker who controls the mint's freeze authority can freeze the coin or pc vault at any time after other users have deposited real liquidity via `process_deposit`, which itself performs no freeze-authority check on the vault mints either: [4](#0-3) 

Once the vault is frozen, `Invokers::token_transfer` calls inside `Deposit`, `Withdraw`, and all four swap instructions targeting that vault will fail at the SPL Token program level, and since these instructions move both vault sides atomically, freezing just one vault (even the attacker's own malicious-mint side) blocks the swap/deposit/withdraw path for the entire pool, including the legitimate token side and any depositors' pooled funds.

### Impact Explanation
This permanently and unrecoverably locks pooled funds: any user who deposits real value into a pool created against a malicious mint can have their LP-backing assets (both sides of the pool) frozen out of reach forever, mirroring the "permanent freezing of user or LP funds" impact category. There is no recovery instruction in the program to change a vault's mint or bypass a frozen SPL account.

### Likelihood Explanation
`Initialize2` can be invoked by any unprivileged wallet with attacker-chosen accounts in a single transaction; creating a mint with a freeze authority (and later signing a `FreezeAccount` instruction) requires no special privilege. Since `Deposit`/`Swap` are open to any user who is not aware the mint carries a freeze authority, the attack is straightforward and requires no cooperation from Raydium or the victim beyond normal pool usage.

### Recommendation
Add the same guard already used for `lp_mint` to `amm_coin_mint_info` and `amm_pc_mint_info` in `process_initialize2`: reject pool creation (`AmmError::InvalidFreezeAuthority`) if either mint's `freeze_authority` is `Some(_)`. Consider also re-validating (or documenting the trust assumption) in `process_deposit` and the swap paths, since new pools can be created for pre-existing mints whose freeze authority could be set/rotated after pool creation if the SPL token allows freeze-authority reassignment.

### Proof of Concept
1. Attacker creates `mint_A` with `freeze_authority = attacker` and mints supply to themselves.
2. Attacker calls `Initialize2` with `amm_coin_mint = mint_A` and `amm_pc_mint` = a legitimate token (e.g. USDC), seeding the pool with some `mint_A` and USDC — this passes all current checks since only `lp_mint.freeze_authority` is validated.
3. Victims see a normal-looking pool and call `Deposit`/`Swap`, sending real USDC into the pc vault.
4. Attacker calls the SPL Token `FreezeAccount` instruction (signed by `attacker` as freeze authority) on the `amm_coin_vault` (holding `mint_A`).
5. Any subsequent `Withdraw`/`Swap`/`Deposit` referencing this pool now fails at the token-transfer CPI because the frozen coin vault cannot be debited/credited, permanently locking the victims' USDC (and all coin-side funds) inside the pool.

### Citations

**File:** program/src/processor.rs (L776-802)
```rust
        Self::generate_amm_associated_spl_token(
            program_id,
            spl_token_program_id,
            market_info,
            amm_coin_vault_info,
            amm_coin_mint_info,
            user_wallet_info,
            system_program_info,
            rent_sysvar_info,
            token_program_info,
            amm_authority_info,
            COIN_VAULT_ASSOCIATED_SEED,
        )?;
        // create pc vault account
        Self::generate_amm_associated_spl_token(
            program_id,
            spl_token_program_id,
            market_info,
            amm_pc_vault_info,
            amm_pc_mint_info,
            user_wallet_info,
            system_program_info,
            rent_sysvar_info,
            token_program_info,
            amm_authority_info,
            PC_VAULT_ASSOCIATED_SEED,
        )?;
```

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

**File:** program/src/processor.rs (L1109-1125)
```rust
        check_assert_eq!(
            *token_program_info.key,
            spl_token::id(),
            "spl_token_program",
            AmmError::InvalidSplTokenProgram
        );
        let spl_token_program_id = token_program_info.key;
        // token_coin must be amm.coin_vault or token_source_coin must not be amm.coin_vault
        if *amm_coin_vault_info.key != amm.coin_vault
            || *user_source_coin_info.key == amm.coin_vault
        {
            return Err(AmmError::InvalidCoinVault.into());
        }
        // token_pc must be amm.pc_vault or token_source_pc must not be amm.pc_vault
        if *amm_pc_vault_info.key != amm.pc_vault || *user_source_pc_info.key == amm.pc_vault {
            return Err(AmmError::InvalidPCVault.into());
        }
```
