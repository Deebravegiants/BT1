## Title
Missing Freeze-Authority Check on Coin/PC Mints Allows Permanent Freezing of Pool Funds via a Malicious/Freezable Token - (File: `program/src/processor.rs`)

## Summary
`Initialize2` validates that the **LP mint** has no freeze authority, but performs no equivalent check on the **coin_mint** or **pc_mint** that back the pool's vaults. Since pool creation is permissionless, an attacker can create a pool using a mint they (or a colluding party) control the freeze authority for, then freeze the AMM's vault token account at will. Because the AMM authority cannot thaw an account frozen by an external mint's freeze authority, this permanently blocks `Deposit`, `Withdraw`, `WithdrawPnl`, and all swap instructions for that pool, freezing any liquidity supplied by unrelated LPs — the same failure mode described in the source report where a pausable token DoSes settlement/liquidation flows and creates insolvency/fund-freezing risk.

## Finding Description
In `process_initialize2`, the coin and pc mints are unpacked with no freeze-authority validation: [1](#0-0) 

Compare this to the LP mint, which is explicitly checked and rejected if it has a freeze authority: [2](#0-1) 

The vaults for coin/pc are then created as ordinary SPL Token accounts owned by the AMM `$authority` PDA: [3](#0-2) 

All subsequent flows — `Deposit` (program/src/processor.rs:1327-1340), `Withdraw` (program/src/processor.rs:1787-1804), `WithdrawPnl` (program/src/processor.rs:1509-1526), and all four swap instructions (program/src/processor.rs:2006-2046, 2212-2258, 2402-2447, 2591-2637) — rely on plain `spl_token::instruction::transfer` CPIs via `Invokers::token_transfer`/`token_transfer_with_authority`: [4](#0-3) 

A classic SPL Token account can be frozen by its mint's freeze authority at any time, independent of the AMM authority PDA. If the coin/pc mint carries an active freeze authority, that authority (fully controlled off-chain by the pool creator or any party they collude with) can freeze the AMM's coin or pc vault token account. Every subsequent `spl_token::instruction::transfer` involving that vault will fail with `AccountFrozen`, and since Solana transactions are atomic, every `Deposit`, `Withdraw`, `WithdrawPnl`, and swap instruction touching that pool will revert.

## Impact Explanation
Because pool creation via `Initialize2` is permissionless and reachable by any unprivileged user with attacker-chosen mint accounts, an attacker can:
1. Create a pool with a coin or pc mint whose freeze authority they control.
2. Wait for unrelated LPs to deposit liquidity into the AMM's vaults via `Deposit`.
3. Freeze the vault token account using the mint's freeze authority (an operation outside program control).
4. Permanently block `Withdraw`/`WithdrawPnl`/swaps for that pool, trapping all deposited coin/pc tokens in the frozen vault indefinitely — the AMM `$authority` PDA has no ability to thaw an account frozen by an external freeze authority.

This is a permanent freezing of LP/user funds in the vault, matching the report's core impact category (protocol insolvency risk / flow DoS), and is strictly worse than the ERC20-pause analog because freezing here is targeted, attacker-controlled, and irreversible from the program's perspective (no auto-unpause).

## Likelihood Explanation
Likelihood is Medium-to-High relative to the external report's "rare, non-attacker-triggerable" pause event: here the freeze is fully attacker-controlled and triggerable at will by the malicious pool creator, requiring only that other users be lured into depositing into an apparently normal-looking pool with a freezable mint (a scenario common in permissionless AMMs). No privileged program access or validator collusion is required — only ordinary `Initialize2`/`Deposit`/freeze-authority actions by an unprivileged actor.

## Recommendation
In `process_initialize2`, after unpacking `coin_mint` and `pc_mint`, reject pool creation if either mint has a freeze authority set, mirroring the existing LP-mint check:
```rust
if coin_mint.freeze_authority.is_some() {
    return Err(AmmError::InvalidFreezeAuthority.into());
}
if pc_mint.freeze_authority.is_some() {
    return Err(AmmError::InvalidFreezeAuthority.into());
}
```
Alternatively/additionally, since the underlying transfers cannot distinguish a transient pause from a permanent freeze, consider supporting partial/queued withdrawal paths so a frozen vault does not block unrelated instructions indefinitely, and clearly documenting freeze-authority risk for pool creators/integrators of arbitrary SPL tokens.

## Proof of Concept
1. Attacker mints `EvilCoin` (SPL Token, classic Token program) with `freeze_authority = attacker_key`.
2. Attacker calls `Initialize2` pairing `EvilCoin` with a legitimate `pc_mint` (e.g., USDC), supplying initial liquidity. `process_initialize2` only checks `lp_mint.freeze_authority.is_some()` (program/src/processor.rs:904-906) — no check exists for `coin_mint`/`pc_mint`, so pool creation succeeds.
3. Victim LPs call `Deposit`, transferring `EvilCoin`/USDC into `amm_coin_vault`/`amm_pc_vault` (program/src/processor.rs:1327-1340).
4. Attacker, using `attacker_key` as `EvilCoin`'s freeze authority, sends an SPL Token `FreezeAccount` instruction directly against `amm_coin_vault_info` (a normal SPL token account, not specially protected).
5. Any subsequent `Withdraw`, `WithdrawPnl`, or swap instruction touching `amm_coin_vault` now fails inside `Invokers::token_transfer_with_authority`'s `spl_token::instruction::transfer` CPI (program/src/invokers.rs:170-195) with `AccountFrozen`, permanently reverting the transaction and trapping victim LP funds in the vault.

### Citations

**File:** program/src/processor.rs (L742-745)
```rust
        // unpack and check coin_mint
        let coin_mint = Self::unpack_mint(&amm_coin_mint_info, spl_token_program_id)?;
        // unpack and check pc_mint
        let pc_mint = Self::unpack_mint(&amm_pc_mint_info, spl_token_program_id)?;
```

**File:** program/src/processor.rs (L775-802)
```rust
        // create coin vault account
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

**File:** program/src/invokers.rs (L147-195)
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
