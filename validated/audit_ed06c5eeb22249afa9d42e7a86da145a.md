### Title
No emergency/rescue withdraw path when pool coin/pc mint has a freeze/blacklist authority, permanently locking LP funds - (File: `program/src/processor.rs`)

### Summary
`Initialize2` explicitly rejects an LP mint with a freeze authority, but performs no equivalent check on the pool's `coin_mint`/`pc_mint`. If a pool is created with an underlying token that carries a freeze/blacklist authority (e.g. a "SnailBrook"-style blacklistable SPL token), any LP whose destination coin/pc token account (or wallet) later gets frozen can never successfully call `Withdraw` again — the mandatory SPL `Transfer` CPI to that account will always fail, and the program has no admin/emergency withdrawal instruction to rescue or unwind that position.

### Finding Description
During pool creation, `process_initialize2` unpacks the LP mint and enforces: [1](#0-0) 
```
let lp_mint = Self::unpack_mint(&amm_lp_mint_info, spl_token_program_id)?;
...
if lp_mint.freeze_authority.is_some() {
    return Err(AmmError::InvalidFreezeAuthority.into());
}
```
No analogous check exists for `coin_mint` or `pc_mint`, which are unpacked only for decimals/mint-match purposes: [2](#0-1) 

Because the underlying token mints are never validated to be free of a freeze authority, a pool can legitimately be created (and swapped/deposited into by unprivileged users) around a token that can blacklist/freeze arbitrary holder accounts.

In `process_withdraw`, redemption of LP tokens is atomic: it burns the user's LP tokens **and** transfers both coin and pc amounts out of the vaults to the user's destination accounts in the same instruction: [3](#0-2) 
```
Invokers::token_transfer_with_authority(
    token_program_info.clone(),
    amm_coin_vault_info.clone(),
    user_dest_coin_info.clone(),
    ...
)?;
Invokers::token_transfer_with_authority(
    token_program_info.clone(),
    amm_pc_vault_info.clone(),
    user_dest_pc_info.clone(),
    ...
)?;
Invokers::token_burn(
    token_program_info.clone(),
    user_source_lp_info.clone(),
    amm_lp_mint_info.clone(),
    source_lp_owner_info.clone(),
    withdraw.amount,
)?;
```
The transfer is issued via the standard `spl_token::instruction::transfer` CPI: [4](#0-3) 

If the destination coin or pc token account (or the owning wallet, for tokens that also gate by owner) has been frozen/blacklisted by the mint's freeze authority, this CPI reverts unconditionally, causing the entire `Withdraw` transaction — including the LP burn — to fail. `process_deposit` has the identical pattern (mint check only for `pc_vault_mint == coin_vault_mint`, no freeze-authority check) at: [5](#0-4) 

Scanning `program/src/processor.rs`'s dispatcher, there is no owner/emergency-rescue instruction analogous to the recommendation in the report — the only privileged instructions are `SetParams`, `WithdrawPnl`, and config management, none of which allow rescuing a specific LP's stuck vault share: [6](#0-5) 

### Impact Explanation
An LP whose account is frozen/blacklisted on the coin or pc mint after depositing has no way to ever redeem their LP tokens: every future `Withdraw` call reverts at the `token_transfer_with_authority` step, so the LP burn never executes and the position is permanently unredeemable. This is a genuine, protocol-level permanent freezing of user LP funds with no mitigation path in the program (no admin rescue instruction exists at all, unlike the recommendation in the referenced report).

### Likelihood Explanation
Likelihood depends on the AMM being deployed for a coin/pc mint that carries an active freeze/blacklist authority — which the program does not prevent, since only the LP mint's freeze authority is checked at `Initialize2`. Any permissionless pool creator can pick arbitrary `coin_mint`/`pc_mint` pairs, and once real-world blacklistable tokens (increasingly common for compliance-driven or "rug-protection" tokens) are paired into a pool, any depositor risks having their position permanently frozen if their account is later blacklisted, whether justified or erroneous.

### Recommendation
Either (a) at `Initialize2`, reject `coin_mint`/`pc_mint` that have a non-null `freeze_authority`, consistent with the existing `lp_mint.freeze_authority.is_some()` check, or (b) introduce a privileged emergency-withdraw/rescue instruction (guarded by a trusted multisig/timelock, as the original report recommends) that lets governance recover a specific stranded vault balance and settle/mark the affected LP position, so funds are not lost indefinitely for reasons outside any single user's control.

### Proof of Concept
1. Create a pool via `Initialize2` using a coin (or pc) mint with an active `freeze_authority` (SPL Token supports freezing token accounts) — this succeeds because only `lp_mint.freeze_authority` is checked (`program/src/processor.rs:904-906`).
2. User A deposits via `Deposit`, receiving LP tokens (`program/src/processor.rs:1327-1350`).
3. The mint's freeze authority freezes User A's coin (or pc) token account, or blacklists User A's wallet at the token-program-extension level (as in blacklist-style tokens).
4. User A calls `Withdraw`; `Invokers::token_transfer_with_authority` to `user_dest_coin_info` fails because the destination account is frozen, causing the whole instruction (including the LP burn) to fail (`program/src/processor.rs:1787-1812`).
5. There is no other instruction in `Processor::process` (`program/src/processor.rs:2984-3052`) that allows User A or the program owner to recover the underlying share — the LP tokens and the corresponding vault share are permanently stuck.

### Citations

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

**File:** program/src/processor.rs (L1076-1079)
```rust
        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        if amm.pc_vault_mint == amm.coin_vault_mint {
            return Err(AmmError::NotAllowed.into());
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

**File:** program/src/processor.rs (L3013-3020)
```rust
            AmmInstruction::SetParams(setparams) => {
                Self::process_set_params(program_id, accounts, setparams)
            }
            AmmInstruction::WithdrawPnl => Self::process_withdrawpnl(program_id, accounts),
            AmmInstruction::WithdrawSrm(_withdrawsrm) => {
                msg!("This instruction is not supported");
                return Err(AmmError::InvalidInstruction.into());
            }
```

**File:** program/src/invokers.rs (L171-195)
```rust
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
