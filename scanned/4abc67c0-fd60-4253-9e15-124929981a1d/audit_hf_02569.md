# [C] Lock pool can be DoSed

## Summary
Severity: Critical
Contest weight: 0.1001
Dataset id: 13832
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the lock_pool instruction, the creation of an Associated Token Account (ATA) for LP tokens relies on checking the lamport balance to determine if the account exists. The check ctx.accounts.escrow_vault.get_lamports() == 0 is used to decide whether to create the ATA.
```rust
if ctx.accounts.escrow_vault.get_lamports() == 0 {
    associated_token::create(CpiContext::new(
        ctx.accounts.associated_token_program.to_account_info(),
        associated_token::Create {
            payer: ctx.accounts.payer.to_account_info(),
            associated_token: ctx.accounts.escrow_vault.to_account_info(),
            authority: ctx.accounts.lock_escrow.to_account_info(),
            mint: ctx.accounts.lp_mint.to_account_info(),
            token_program: ctx.accounts.token_program.to_account_info(),
            system_program: ctx.accounts.system_program.to_account_info(),
        }
    )
}
```
This is problematic because:
An attacker can prevent ATA creation by sending SOL to the escrow_vault address beforehand
Having SOL in an address doesn't guarantee a properly initialized Token Account
Without a properly initialized ATA, the locking mechanism would fail since there would be no valid token account to receive the LP tokens
As a result, the lock pool would be DoSed.

## Recommendation
Replace the current implementation with create_idempotent which safely handles ATA creation regardless of lamport balance.
