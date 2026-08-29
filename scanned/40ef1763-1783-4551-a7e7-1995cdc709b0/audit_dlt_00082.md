# [H] Program<'info, System> is not properly validated

## Summary
Severity: High
Chain: Solana
Component: coral-xyz/anchor
CVE: CVE-2026-45137
CWE: Improper Input Validation
Published: 2026-05-07
Source: https://github.com/otter-sec/anchor/security/advisories/GHSA-c6rc-8jpp-2fgc
Type: github-advisory

## Details
### Summary
An logic error causes anchor programs to accept any program id when requiring the system program id, causing false assumptions resulting in potential arbitrary cpi in programs that invoke system program instructions.

### Details
In the TryFrom<&'a AccountInfo<'a>> implementation for Program<'a, T>, the id of T is compared with Pubkey::default() to check whether anchor should allow any executable account, or a specific account, because when no T is supplied, T defaults to (), which implements Id::id() by returning Pubkey::default(). This results in T = () and T = System (which has Pubkey::default() as the id) having the same behavior, both allow any executable account. Programs built with anchor assume that the anchor runtime verifies passed in programs of type Program<'a, System> are in fact the system program. This false assumption can lead to arbitrary CPI or payment bypassing when programs try making CPI calls to the system program using the passed in system program due to the fact that the attacker can pass in any program instead of the system program.

https://github.com/solana-foundation/anchor/blob/5ff3f96eeda91cc54b7fa525631eb8c1394fda04/lang/src/accounts/program.rs#L148-L163

### PoC
Build and deploy the following anchor program:
```rs
/// victim.rs
/// an anchor program that uses the system program in some way.

use anchor_lang::prelude::*;
use anchor_lang::prelude::program::invoke;
use anchor_lang::prelude::instruction::Instruction;

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(mut)]
    pub sender: Signer<'info>,
    #[account(mut)]
    pub recipient: SystemAccount<'info>,
    // the "System" part here should ensure that callers can only pass the system program.
    pub system_program: Program<'info, System>,
}

pub fn handler(ctx: Context<Initialize>, amount: u64) -> Result<()> {
    // this should be the system program id, but due to an issue in the validation logic, this could be any program id.
    msg!("System program: {:?}", ctx.accounts.system_program.key());

    // construct a transfer instruction
    // note that not only raw instructions, but also any other instruction
    // builders that properly forward the passed in program id are vulnerable.
    let mut data = Vec::new();
    data.extend_from_slice(&[2, 0, 0, 0]);  // transfer discriminator
    data.extend_from_slice(&amount.to_le_bytes());  // amount
```

_Trimmed to 38 lines — full report: https://github.com/otter-sec/anchor/security/advisories/GHSA-c6rc-8jpp-2fgc_
