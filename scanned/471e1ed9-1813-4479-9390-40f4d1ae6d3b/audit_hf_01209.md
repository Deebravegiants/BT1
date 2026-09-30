# [C] Attacker can become the authority of the config account

## Summary
Severity: Critical
Contest weight: 0.1173
Dataset id: 5380
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The initialize_extra_account_meta_list instruction doesn't check if payer is the current authority of an existing config account. It directly sets payer as the new authority. This lets anyone become the authority by calling this instruction with a new token mint.

## Recommendation
Only set Config::authority at the time of initialization and ensure that payer is authority. Replace:
ctx.accounts.config.authority = ctx.accounts.payer.key();
With:
if ctx.accounts.config.authority == Pubkey::default() {
    // only set at initialization
    ctx.accounts.config.authority = ctx.accounts.payer.key();
}
require_keys_eq!(ctx.accounts.config.authority, ctx.accounts.payer.key());
