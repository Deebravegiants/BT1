# [M] Lack of Account Check in EditLocker

## Summary
Severity: Medium
Contest weight: 0.4247
Dataset id: 12742
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By design, PinkLock Solana allows the locker owner to modify the associated locker information, including the amount. When the locked amount is increased, there is a need to transfer additional funds from the user's account to the vault. While examining the topup logic, we notice the associated implementation can be improved. In the following, we show the code snippet of the related EditLocker data structure. The user_token_account is the account passed in by the user, and its mint amount must match the mint of the SPL token that will be locked, i.e., constraint = user_token_account.mint == mint.key(). Apparently, this constraint is currently missing.
```solidity
pub struct EditLocker<'info> {
    #[account(mut)]
    pub locker: Box<Account<'info, Locker>>,
    #[account(
        constraint = mint.key() == locker.mint,
        token::token_program = token_program,
    )]
    pub mint: Box<InterfaceAccount<'info, Mint>>,
    #[account(mut, constraint = locker_vault.key() == locker.vault)]
    pub locker_vault: Box<InterfaceAccount<'info, TokenAccount>>,
    #[account(
        mut,
        constraint = locker_vault.key() == locker.vault && locker_vault.mint == locker.mint,
        token::token_program = token_program,
    )]
    pub user_token_account: Box<InterfaceAccount<'info, TokenAccount>>,
}
```

## Recommendation
Add the mint validation in the above EditLocker data structure.
