## Title
Missing freeze-authority check on coin/pc mints allows permanent freezing of pool vaults - (File: `program/src/processor.rs`)

## Summary
`process_initialize2` validates that the **LP mint** has no `freeze_authority` before creating a pool, but never validates that the **coin_mint** or **pc_mint** (the actual collateral/liquidity tokens deposited into the pool's vaults) are free of an active `freeze_authority`. Any pool creator can therefore permanently register a pool for a mint whose freeze authority can later freeze the AMM's `coin_vault`/`pc_vault` token accounts, DoSing deposit/withdraw/swap for all users of that pool.

## Finding Description
In `process_initialize2`, the coin and pc mints are unpacked with `Self::unpack_mint` and their vaults are checked for `delegate` and `close_authority`, but the mint's `freeze_authority` field is never inspected: [1](#0-0) 

Only the newly created LP mint is checked for `freeze_authority`: [2](#0-1) 

The coin/pc vaults are checked for `delegate` and `close_authority` but not for the freeze status of their underlying mint: [3](#0-2) 

This check is entirely absent from every reachable, unprivileged instruction that touches these vaults — `process_initialize2`, `process_deposit`/`process_withdraw` (both rely on the same `coin_vault_mint`/`pc_vault_mint` recorded at init), and all four swap paths (`process_swap_base_in`, `process_swap_base_out`, `process_swap_base_in_v2`, `process_swap_base_out_v2`), none of which re-validate freeze authority either: [4](#0-3) [5](#0-4) 

A grep of the whole program confirms `freeze_authority` is referenced exactly once in the codebase (the LP-mint check), never for `amm_coin_mint_info`/`amm_pc_mint_info`.

## Impact Explanation
Since `Initialize2` is callable by any unprivileged user with attacker-chosen `coin_mint`/`pc_mint` accounts, a pool creator can register a pool using a token whose mint still has an active `freeze_authority` (a normal, common configuration for many SPL tokens, e.g. regulated/stablecoin-style tokens). Whoever controls that mint's `freeze_authority` can subsequently issue `FreezeAccount` against the AMM's `coin_vault` or `pc_vault` PDA-owned token account. Once frozen:
- `Deposit`/`Withdraw` transfers into/out of the vault fail.
- All four swap instructions (`SwapBaseIn/Out`, `SwapBaseIn/OutV2`) fail because they move tokens through the same frozen vault.
- Because the vault is a PDA owned by the AMM authority (not the pool creator), there is no on-chain recourse: liquidity providers' deposited funds become permanently locked, and other users cannot withdraw or trade.

This matches the reported bug class exactly (Medium severity per the referenced judge comment): rare but avoidable, with concrete permanent freezing of pooled user/LP funds.

## Likelihood Explanation
Likelihood is low-to-moderate: it requires either (a) a malicious/careless pool creator picking a freeze-capable mint (which is easy — nothing prevents it), combined with (b) that mint's freeze authority actually exercising it. However, the check exists for the LP mint precisely because the protocol already recognizes this class of risk; the same protection was simply not extended to the coin/pc collateral mints, despite them being the tokens actually held at risk in the vaults.

## Recommendation
In `process_initialize2`, after unpacking `coin_mint` and `pc_mint`, reject pool creation if either mint has `freeze_authority.is_some()`, mirroring the existing LP-mint check:
```rust
if coin_mint.freeze_authority.is_some() || pc_mint.freeze_authority.is_some() {
    return Err(AmmError::InvalidFreezeAuthority.into());
}
```
This closes the gap at the only point where a malicious/risky mint can be introduced into a pool, protecting downstream `Deposit`, `Withdraw`, and all swap instructions from this permanent-freeze DoS vector.

## Proof of Concept
1. Create an SPL mint `M` and set its `freeze_authority` to attacker-controlled key `F` (do not set to `None`).
2. Call `Initialize2` (`program/src/processor.rs::process_initialize2`) using `M` as `amm_coin_mint_info` (or `amm_pc_mint_info`). The instruction succeeds: the coin-mint check only inspects `unpack_mint` for owner/format, not `freeze_authority`.
3. Pool operates normally; users deposit into `amm_coin_vault` via `Deposit`.
4. Attacker (holder of `F`) issues `spl_token::instruction::freeze_account` against the pool's `coin_vault` token account.
5. Any subsequent `Deposit`, `Withdraw`, `SwapBaseIn`, `SwapBaseOut`, `SwapBaseInV2`, or `SwapBaseOutV2` transaction touching that vault now fails at the SPL Token CPI level, permanently locking all liquidity in the pool since the vault authority is a program PDA with no ability to thaw the account.

### Citations

**File:** program/src/processor.rs (L742-745)
```rust
        // unpack and check coin_mint
        let coin_mint = Self::unpack_mint(&amm_coin_mint_info, spl_token_program_id)?;
        // unpack and check pc_mint
        let pc_mint = Self::unpack_mint(&amm_pc_mint_info, spl_token_program_id)?;
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

**File:** program/src/processor.rs (L1843-1876)
```rust
    pub fn process_swap_base_in(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        swap: SwapInstructionBaseIn,
    ) -> ProgramResult {
        const ACCOUNT_LEN: usize = 17;
        let input_account_len = accounts.len();
        if input_account_len != ACCOUNT_LEN && input_account_len != ACCOUNT_LEN + 1 {
            return Err(AmmError::WrongAccountsNumber.into());
        }
        let account_info_iter = &mut accounts.iter();
        let token_program_info = next_account_info(account_info_iter)?;

        let amm_info = next_account_info(account_info_iter)?;
        let amm_authority_info = next_account_info(account_info_iter)?;
        let _amm_open_orders_info = next_account_info(account_info_iter)?;
        if input_account_len == ACCOUNT_LEN + 1 {
            let _amm_target_orders_info = next_account_info(account_info_iter)?;
        }
        let amm_coin_vault_info = next_account_info(account_info_iter)?;
        let amm_pc_vault_info = next_account_info(account_info_iter)?;

        let _market_program_info = next_account_info(account_info_iter)?;

        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        if amm.pc_vault_mint == amm.coin_vault_mint {
            return Err(AmmError::NotAllowed.into());
        }
        let _market_info = next_account_info(account_info_iter)?;
        let _market_bids_info = next_account_info(account_info_iter)?;
        let _market_asks_info = next_account_info(account_info_iter)?;
        let _market_event_queue_info = next_account_info(account_info_iter)?;
        let _market_coin_vault_info = next_account_info(account_info_iter)?;
        let _market_pc_vault_info = next_account_info(account_info_iter)?;
```

**File:** program/src/processor.rs (L2266-2311)
```rust
    pub fn process_swap_base_in_v2(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        swap: SwapInstructionBaseIn,
    ) -> ProgramResult {
        let account_info_iter = &mut accounts.iter();
        let token_program_info = next_account_info(account_info_iter)?;
        let amm_info = next_account_info(account_info_iter)?;
        let amm_authority_info = next_account_info(account_info_iter)?;
        let amm_coin_vault_info = next_account_info(account_info_iter)?;
        let amm_pc_vault_info = next_account_info(account_info_iter)?;
        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        if amm.pc_vault_mint == amm.coin_vault_mint {
            return Err(AmmError::NotAllowed.into());
        }
        let user_source_info = next_account_info(account_info_iter)?;
        let user_destination_info = next_account_info(account_info_iter)?;
        let user_source_owner = next_account_info(account_info_iter)?;
        if !user_source_owner.is_signer {
            return Err(AmmError::InvalidSignAccount.into());
        }
        check_assert_eq!(
            *token_program_info.key,
            spl_token::id(),
            "spl_token_program",
            AmmError::InvalidSplTokenProgram
        );
        let spl_token_program_id = token_program_info.key;
        if *amm_authority_info.key
            != Self::authority_id(program_id, AUTHORITY_AMM, amm.nonce as u8)?
        {
            return Err(AmmError::InvalidProgramAddress.into());
        }
        check_assert_eq!(
            *amm_coin_vault_info.key,
            amm.coin_vault,
            "coin_vault",
            AmmError::InvalidCoinVault
        );
        check_assert_eq!(
            *amm_pc_vault_info.key,
            amm.pc_vault,
            "pc_vault",
            AmmError::InvalidPCVault
        );

```
