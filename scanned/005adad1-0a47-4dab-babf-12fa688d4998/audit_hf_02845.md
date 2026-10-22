# [C] deposit_ico_in_ata() overwrites the total supply instead of adding to the total amount

## Summary
Severity: Critical
Contest weight: 0.1041
Dataset id: 15852
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deposit_ico_in_ata function allows the admin to add more ICO tokens to the programʼs associated token account (ATA). This ensures that the ICO can continue with an increased supply of tokens.
```sol
pub fn deposit_ico_in_ata(ctx: Context<DepositIcoInATA>, ico_amount:
u64) -> ProgramResult {
    if ctx.accounts.data.admin != *ctx.accounts.admin.key {
        return Err(ProgramError::IncorrectProgramId);
    }
    // transfer ICO admin to program ata
    let cpi_ctx = CpiContext::new(
        ctx.accounts.token_program.to_account_info(),
        token::Transfer {
            from: ctx.accounts.ico_ata_for_admin.to_account_info(),
            to: ctx.accounts.ico_ata_for_ico_program.to_account_info(),
            authority: ctx.accounts.admin.to_account_info(),
        },
    );
    token::transfer(cpi_ctx, ico_amount)?;
    let data = &mut ctx.accounts.data;
    data.total_amount = ico_amount;
    msg!("deposit {} ICO in program ATA.", ico_amount);
```
The problem here is that the line data.total_amount = ico_amount; in the deposit_ico_in_ata() function overrides the total_amount field with the new ico_amount rather than adding to the existing amount. This design flaw causes the total token amount to reset with each new deposit, leading to the loss of previous deposit records.

## Recommendation
Replace data.total_amount = ico_amount; with data.total_amount += ico_amount; to correctly accumulate the total ICO token supply across multiple deposits. This ensures accurate tracking of the total tokens available for the ICO.
