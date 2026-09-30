# [H] rebate_info and rebate_manager are unable to

## Summary
Severity: High
Contest weight: 0.3127
Dataset id: 1736
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
rebate_info and rebate_manager will not be able to sign the CPI message because the implementation of the seeds function is incorrect because the correct seed needs to include the full seed phrase and the bump, but the seeds function does not include the bump.
622e8c44ae2f8cd4219c7c2a0181f25ca0/WOOFi_Solana/programs/rebate_manager/src/state/rebate_manager.rs#L54
```rust
pub fn seeds(&self) -> [&[u8]; 2] {
    [
        REBATEMANAGER_SEED.as_bytes(),
        self.quote_token_mint.as_ref(),
    ]
}
```
622e8c44ae2f8cd4219c7c2a0181f25ca0/WOOFi_Solana/programs/rebate_manager/src/state/rebate_info.rs#L51
```rust
pub fn seeds(&self) -> [&[u8]; 3] {
    [
        REBATEINFO_SEED.as_bytes(),
        self.rebate_manager.as_ref(),
        self.rebate_authority.as_ref(),
    ]
}
```
Internal pre-conditions
None
External pre-conditions
None
Attack Path
None
It will prevent the claim_rebate_fee and withdraw operations from executing, resulting in tokens being permanently locked in the contract.

## Recommendation
Here is an example of fixing rebate_manager:
```rust
#[account]
#[derive(InitSpace)]
pub struct RebateManager {
    pub authority: Pubkey, // 32
    #[max_len(ADMIN_AUTH_MAX_LEN)]
    pub admin_authority: Vec<Pubkey>,
    pub quote_token_mint: Pubkey, // 32
    pub token_vault: Pubkey, // 32
    pub rebate_manager_bump: [u8; 1],
}
pub fn seeds(&self) -> [&[u8]; 2] {
    [
        REBATEMANAGER_SEED.as_bytes(),
        self.quote_token_mint.as_ref(),
        self.rebate_manager_bump.as_ref(),
    ]
}
pub fn initialize(
    &mut self,
    authority: Pubkey,
    quote_token_mint: Pubkey,
    token_vault: Pubkey,
    bump: u8,
) -> Result<()> {
    self.authority = authority;
    self.quote_token_mint = quote_token_mint;
    self.token_vault = token_vault;
    self.rebate_manager_bump = [bump];
    Ok(())
}
pub fn handler(ctx: Context<CreateRebateManager>) -> Result<()> {
    let authority = ctx.accounts.authority.key();
    let quote_token_mint = ctx.accounts.quote_token_mint.key();
    let token_vault = ctx.accounts.token_vault.key();
    let bump = ctx.bumps.rebate_manager;
    let rebate_manager = &mut ctx.accounts.rebate_manager;
    rebate_manager.initialize(authority, quote_token_mint, token_vault, bump);
}
```
The fix for rebate_info is the same as described above.
