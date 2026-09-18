## Analysis Result

The report requests a token allowlist to block unsafe SPL mint behaviors before they can be used with the AMM. The strongest analog reachable by an unprivileged pool creator in this Raydium fork is: **`process_initialize2` never validates that the `coin`/`pc` mints have no freeze authority**, even though it explicitly does this exact check for the `lp_mint`.

### Title
Missing freeze-authority check on coin/pc mints in `Initialize2` allows permanent freezing of pooled funds - ([File: program/src/processor.rs])

### Summary
`Processor::process_initialize2` unpacks and validates the coin and pc mints, but only rejects a freeze authority on the newly created `lp_mint`. It never checks `coin_mint.freeze_authority` or `pc_mint.freeze_authority`, so any user can permissionlessly create a pool using a mint they control the freeze authority for.

### Finding Description
In `process_initialize2`, the coin and pc mints are unpacked with `Self::unpack_mint` and only checked for basic properties (mismatch between coin/pc mint, vault ownership, delegate, close authority), while freeze authority is validated only for the LP mint: [1](#0-0) 

The coin vault and pc vault (`amm_coin_vault_info`, `amm_pc_vault_info`) are created as regular SPL token accounts owned by the pool's PDA authority, but the SPL Token program still allows the mint's `freeze_authority` to freeze *any* token account of that mint, including the AMM's vaults: [2](#0-1) 

Because there is no allowlist, no check that `coin_mint.freeze_authority`/`pc_mint.freeze_authority` is `None`, and no restriction on who may call `Initialize2`, an attacker can:
1. Create an SPL mint where they retain the freeze authority.
2. Call `Initialize2` to create a Raydium pool pairing that malicious mint with a legitimate token, seeding it with their own initial liquidity so the pool looks normal.
3. Wait for other LPs to deposit via `process_deposit` (which transfers into the same vault accounts) or for swappers to route through the pool.
4. Freeze the coin (or pc) vault token account using the retained freeze authority.

Once frozen, `process_withdraw`, `process_swap_base_in`/`_out` (and v2 variants), and `process_withdrawpnl` all attempt SPL `Transfer`/`Burn` CPIs against the frozen vault via `Invokers::token_transfer_with_authority`/`token_transfer`, which will fail at the SPL Token program level while the account is frozen: [3](#0-2) [4](#0-3) 

This permanently locks all coin/pc tokens in the vault and any LP tokens minted against it, since the AMM program has no mechanism to force-thaw a vault it does not control the freeze authority for.

### Impact Explanation
This results in permanent freezing of user and LP funds in a pool that otherwise passes all of the program's own sanity checks (matching the "delegate is none", "close authority is none" checks already present for vaults, but missing the equivalent freeze-authority check). Any depositor or swapper who is unaware of the malicious mint's freeze authority can have their funds locked indefinitely. This satisfies the "permanent freezing of user or LP funds" acceptance criterion.

### Likelihood Explanation
`Initialize2` is fully permissionless — it only requires `user_wallet_info.is_signer` and payment of the create-pool fee, with no allowlist enforced on `amm_coin_mint_info`/`amm_pc_mint_info`: [5](#0-4) 
Any attacker can mint an SPL token with a freeze authority (a completely normal, permitted feature of the SPL Token program) and immediately create a pool with it in one transaction, making this trivially reachable without needing any special privilege in the Raydium program itself.

### Recommendation
In `process_initialize2`, after unpacking `coin_mint` and `pc_mint`, add the same freeze-authority check already applied to `lp_mint`:
```rust
if coin_mint.freeze_authority.is_some() {
    return Err(AmmError::InvalidFreezeAuthority.into());
}
if pc_mint.freeze_authority.is_some() {
    return Err(AmmError::InvalidFreezeAuthority.into());
}
```
placed alongside the existing checks at [6](#0-5) , mirroring the check already performed at [7](#0-6) . More broadly, consider a governance-maintained mint allowlist/denylist for pool creation, consistent with the original report's recommendation.

### Proof of Concept
1. Attacker creates SPL mint `M` via `spl_token::instruction::initialize_mint`, setting themselves as `freeze_authority`.
2. Attacker mints some `M` and pairs it with e.g. USDC, calling `initialize2` (program/src/instruction.rs `initialize2`) to create a Raydium pool with `amm_coin_mint = M`.
3. Legitimate LPs deposit USDC/`M` into the pool via `Deposit`, increasing `amm_pc_vault`/`amm_coin_vault` balances.
4. Attacker calls `spl_token::instruction::freeze_account` on the `M` coin vault (a normal SPL Token instruction, using their retained freeze authority — no interaction with the Raydium program required).
5. Any subsequent `Withdraw`, `SwapBaseIn`, `SwapBaseOut`, or `WithdrawPnl` call touching that vault fails at the SPL Token CPI, permanently locking the USDC and `M` tokens (and burning LP redemption ability) in the pool.

### Citations

**File:** program/src/processor.rs (L684-694)
```rust
        msg!(arrform!(LOG_SIZE, "initialize2: {:?}", init).as_str());
        if !user_wallet_info.is_signer {
            return Err(AmmError::InvalidSignAccount.into());
        }
        check_assert_eq!(
            *token_program_info.key,
            spl_token::id(),
            "spl_token_program",
            AmmError::InvalidSplTokenProgram
        );
        let spl_token_program_id = token_program_info.key;
```

**File:** program/src/processor.rs (L742-745)
```rust
        // unpack and check coin_mint
        let coin_mint = Self::unpack_mint(&amm_coin_mint_info, spl_token_program_id)?;
        // unpack and check pc_mint
        let pc_mint = Self::unpack_mint(&amm_pc_mint_info, spl_token_program_id)?;
```

**File:** program/src/processor.rs (L849-896)
```rust
        // unpack and check token_coin
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

**File:** program/src/processor.rs (L1787-1812)
```rust
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
