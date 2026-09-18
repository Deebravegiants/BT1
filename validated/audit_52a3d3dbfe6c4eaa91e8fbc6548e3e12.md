### Title
Malicious/freezable coin or pc mint accepted at pool creation can permanently freeze LP withdrawals - (File: program/src/processor.rs)

### Summary
`process_initialize2` validates that the LP mint has no freeze authority, but never checks that the pool's `coin_mint`/`pc_mint` are free of a freeze authority. Because `process_withdraw` requires both vault-to-user token transfers to succeed *before* burning the user's LP tokens, a pool creator can permissionlessly create a pool with a coin or pc token they control the freeze authority for, wait for liquidity providers to deposit, and then freeze the AMM's vault token account for that mint. All subsequent withdrawals (and swaps) touching that vault will revert atomically, permanently trapping LP funds with no way to redeem — this is the same bug class as C4 finding M-02 (malicious reward token blocking `withdraw` in FactoryDAO), applied to Raydium's coin/pc vault transfers instead of reward-token transfers.

### Finding Description
`process_initialize2` unpacks and validates the coin/pc mints and vault token accounts but the only freeze-authority check present is on the LP mint: [1](#0-0) 

The coin and pc mints themselves are unpacked with `Self::unpack_mint` but their `freeze_authority` field is never inspected or rejected: [2](#0-1) 

Anyone can permissionlessly call `initialize2` supplying an arbitrary coin/pc mint (subject only to `coin_mint != pc_mint`): [3](#0-2) 

In `process_withdraw`, the coin and pc token transfers out of the AMM vaults are issued via `Invokers::token_transfer_with_authority` and only after both succeed does the code proceed to burn the user's LP tokens and update pool state: [4](#0-3) 

`token_transfer_with_authority` and `token_transfer` simply invoke the SPL Token `Transfer` instruction and propagate any error via `?`: [5](#0-4) 

If the pool creator retains freeze authority on the coin or pc mint, they can later call the standard SPL Token `FreezeAccount` instruction against the pool's `amm_coin_vault` or `amm_pc_vault` token account (owned by the AMM authority PDA — freezing a token account requires only mint freeze authority, not ownership of the account). Once a vault account is frozen, any SPL `Transfer` sourced from it fails, so both `process_withdraw` and the swap instructions (`process_swap_base_in`/`process_swap_base_out`), which perform the identical "transfer-then-continue" pattern, will revert every time: [6](#0-5) [7](#0-6) 

Because the LP burn only occurs after the vault transfer succeeds, there is no `EmergencyWithdraw` or fallback path that lets LPs redeem their share, ignoring the failed transfer — exactly the missing mitigation called out in the referenced report.

### Impact Explanation
Any liquidity provider who deposits into a pool whose coin or pc mint retains a freeze authority is exposed to permanent loss of access to their principal: once the creator freezes the relevant vault token account, `Withdraw` (and both swap instructions) become permanently unusable for that pool, and there is no emergency/ignore-failure code path to recover the other side of the position or to at least redeem the unaffected token. This is a freezing-of-user-funds vulnerability reachable purely through account/data chosen in a single permissionless `Initialize2` transaction plus a subsequent, entirely internal `FreezeAccount` call by the token's freeze authority — no privileged Raydium signer or validator involvement is required.

### Likelihood Explanation
Likelihood is limited by the fact that Raydium restricts the accepted token program to classic `spl_token::id()` (no Token-2022 transfer-hook path is reachable) and by the requirement that a sophisticated/social-engineered LP actually deposit into an attacker-created pool with a mint the attacker controls — similar to the "opt-in pool" caveat the FactoryDAO judge raised for the original finding. However, unlike FactoryDAO's arbitrary "reward token" list, Raydium's coin/pc mints are the core assets being swapped and pooled, so the incentive and practical reachability for an attacker (rug-style pool) is high, and the missing check is a straightforward oversight relative to the existing (but incomplete) LP-mint freeze-authority check already present in the code.

### Recommendation
- In `process_initialize2`, reject coin/pc mints whose `freeze_authority` is `COption::Some(_)`, mirroring the existing check already applied to the LP mint (`program/src/processor.rs:904-906`).
- Alternatively/additionally, add an emergency-withdraw code path that allows LPs to burn their LP tokens and reclaim whichever side of the pool is still transferable, without requiring both `token_transfer_with_authority` calls in `process_withdraw` to succeed atomically.

### Proof of Concept
1. Attacker creates an SPL token mint `M` retaining `freeze_authority = attacker`.
2. Attacker calls `initialize2` (program/src/processor.rs:549) using `M` as `amm_coin_mint`, seeding the pool with real liquidity so it passes the `amm_coin_vault.amount == 0` check (program/src/processor.rs:858-859).
3. Unsuspecting LPs deposit into the pool (`process_deposit`), receiving LP tokens for the `M`/pc pair.
4. Attacker calls the standard SPL Token `FreezeAccount` instruction against the pool's `amm_coin_vault` token account using their freeze authority over `M` (external to the Raydium program, requires only the mint's freeze authority key as signer).
5. Any subsequent `Withdraw` call reaches `Invokers::token_transfer_with_authority` transferring `coin_amount` out of the now-frozen `amm_coin_vault` (program/src/processor.rs:1787-1795); the SPL Token program rejects the transfer, the whole instruction reverts, and the LP burn (program/src/processor.rs:1805-1812) never executes — LPs' deposited principal and previously earned fees are permanently locked in the pool, with `Swap` also reverting identically (program/src/processor.rs:2006-2022).

### Citations

**File:** program/src/processor.rs (L680-682)
```rust
        if *amm_coin_mint_info.key == *amm_pc_mint_info.key {
            return Err(AmmError::InvalidCoinMint.into());
        }
```

**File:** program/src/processor.rs (L742-745)
```rust
        // unpack and check coin_mint
        let coin_mint = Self::unpack_mint(&amm_coin_mint_info, spl_token_program_id)?;
        // unpack and check pc_mint
        let pc_mint = Self::unpack_mint(&amm_pc_mint_info, spl_token_program_id)?;
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

**File:** program/src/processor.rs (L2006-2022)
```rust
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

**File:** program/src/processor.rs (L2402-2424)
```rust
        match swap_direction {
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
```

**File:** program/src/invokers.rs (L170-195)
```rust
    /// Issue a spl_token `Transfer` instruction.
    pub fn token_transfer_with_authority<'a>(
        token_program: AccountInfo<'a>,
        source: AccountInfo<'a>,
        destination: AccountInfo<'a>,
        authority: AccountInfo<'a>,
        amm_seed: &[u8],
        nonce: u8,
        amount: u64,
    ) -> Result<(), ProgramError> {
        let authority_signature_seeds = [amm_seed, &[nonce]];
        let signers = &[&authority_signature_seeds[..]];
        let ix = spl_token::instruction::transfer(
            token_program.key,
            source.key,
            destination.key,
            authority.key,
            &[],
            amount,
        )?;
        solana_program::program::invoke_signed(
            &ix,
            &[source, destination, authority, token_program],
            signers,
        )
    }
```
