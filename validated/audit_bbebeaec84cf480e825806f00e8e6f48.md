### Title
Pool creation lacks a freeze-authority check on `coin_mint`/`pc_mint`, allowing a malicious mint owner to permanently freeze the shared vault and brick Deposit/Withdraw/Swap for all LPs - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` explicitly rejects an LP mint that has a `freeze_authority` set, but it performs no equivalent check on the `coin_mint` or `pc_mint` that back the pool's shared vaults. Any unprivileged user can mint an SPL token with a freeze authority under their control, use it as `coin_mint` or `pc_mint` when calling `Initialize2`, seed the pool, and later call the standard `FreezeAccount` instruction against the AMM's own vault ATA (whose address is deterministically derivable before pool creation). Once frozen, every `Deposit`, `Withdraw`, `SwapBaseIn`/`SwapBaseOut` (and V2 variants) instruction that touches that vault will fail, permanently locking all LPs' and swappers' funds in the pool, not just the attacker's own deposit.

### Finding Description
In `process_initialize2`, the coin/pc mints are unpacked with `unpack_mint` and only checked for coin_mint != pc_mint; no `freeze_authority` check is performed: [1](#0-0) 

By contrast, the LP mint created by the program itself is explicitly checked for the same property, and pool creation is rejected if it is set: [2](#0-1) 

The coin/pc vaults are only checked for `delegate` and `close_authority`, never for whether the underlying mint carries a freeze authority: [3](#0-2) 

Once the pool is live, every fund-moving instruction unconditionally invokes `spl_token::instruction::transfer` against the coin/pc vaults via `Invokers::token_transfer` / `token_transfer_with_authority`, with no fallback or try/catch around a possible failure:
- Deposit: [4](#0-3) 
- Withdraw: [5](#0-4) 
- Swap (base in/out, V1/V2): [6](#0-5) 

If the account holding the freeze authority for `coin_mint`/`pc_mint` calls the standard SPL Token `FreezeAccount` instruction on the AMM's vault token account (an account the AMM program does not, and cannot, control the freeze state of), every subsequent `spl_token::instruction::transfer` against that vault will be rejected by the token program with `AccountFrozen`, causing every instruction above to revert unconditionally. This mirrors the root cause of the referenced OpenQ finding: the protocol does not validate that a token used to fund a shared pool of user/LP value cannot be unilaterally weaponized by its issuer to block transfers, and the failure path has systemic (all-users) blast radius rather than being isolated to the attacker's own funds.

### Impact Explanation
Once a vault is frozen, LP token holders can never call `Withdraw` to redeem their share, and no one can `Swap` through the pool - the pool is permanently bricked and all coin/pc liquidity contributed by every LP (not just the attacker) is frozen indefinitely, since there is no mint-level whitelist or freeze-authority validation and no unfreeze mechanism available to the AMM program or its users. This is a permanent freezing of LP/user funds, matching the High severity bar for this bug class.

### Likelihood Explanation
The attack requires only standard, unprivileged actions: minting an SPL token with a self-controlled freeze authority (no special permission needed), calling `Initialize2` to create a pool with that token as `coin_mint` or `pc_mint`, waiting for other LPs to deposit or swap into it, then submitting a single `FreezeAccount` transaction against the vault ATA. All of these are reachable via ordinary transactions with attacker-chosen accounts and data, requiring no privileged signer, leaked key, or off-chain component.

### Recommendation
In `process_initialize2`, unpack and validate that `coin_mint.freeze_authority` and `pc_mint.freeze_authority` are `COption::None` before allowing pool creation, mirroring the existing check already applied to the LP mint at `program/src/processor.rs:904-906`. Reject pool creation (or require an explicit allow-list/governance-approved mint) if either mint carries a freeze authority.

### Proof of Concept
1. Attacker creates an SPL token mint `M` with `freeze_authority = attacker`.
2. Attacker calls `Initialize2` (`program/src/processor.rs:549`) using `M` as `amm_coin_mint`, funding the pool normally; the vault-creation and mint checks at lines 742-895 pass because none of them inspect `coin_mint.freeze_authority`.
3. Legitimate LPs subsequently call `Deposit` (`program/src/processor.rs:988`) and add liquidity into the same vault.
4. Attacker signs and submits the standard `spl_token::instruction::freeze_account` instruction against `amm_coin_vault` (the ATA derived at `COIN_VAULT_ASSOCIATED_SEED`, computable by the attacker in advance).
5. Any subsequent `Withdraw`, `SwapBaseIn`, or `SwapBaseOut` call fails at the `Invokers::token_transfer*` CPI (e.g. `program/src/processor.rs:1787-1804`, `2006-2022`) with `AccountFrozen`, permanently locking all depositors' funds in the pool.

### Citations

**File:** program/src/processor.rs (L742-745)
```rust
        // unpack and check coin_mint
        let coin_mint = Self::unpack_mint(&amm_coin_mint_info, spl_token_program_id)?;
        // unpack and check pc_mint
        let pc_mint = Self::unpack_mint(&amm_pc_mint_info, spl_token_program_id)?;
```

**File:** program/src/processor.rs (L849-895)
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

**File:** program/src/processor.rs (L1327-1334)
```rust
        Invokers::token_transfer(
            token_program_info.clone(),
            user_source_coin_info.clone(),
            amm_coin_vault_info.clone(),
            source_owner_info.clone(),
            deduct_coin_amount,
        )?;
        Invokers::token_transfer(
```

**File:** program/src/processor.rs (L1787-1804)
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
```

**File:** program/src/processor.rs (L2000-2046)
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
            }
            SwapDirection::PC2Coin => {
                if swap_amount_out >= total_coin_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source pc to amm_pc_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_source_owner.clone(),
                    swap.amount_in,
                )?;
                // withdraw amm_coin_vault to destination coin
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap_amount_out,
                )?;
            }
```
