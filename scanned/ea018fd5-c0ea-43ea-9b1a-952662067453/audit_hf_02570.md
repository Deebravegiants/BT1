# [M] DOS of CreateBondingCurve

## Summary
Severity: Medium
Contest weight: 0.5467
Dataset id: 13854
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The CreateBondingCurve instruction requires passing bonding_curve_token_account:
```solidity
#[account(
    init,
    payer = creator,
    associated_token::mint = mint,
    associated_token::authority = bonding_curve,
)]
pub bonding_curve_token_account: Box<Account<'info, TokenAccount>>,
```
bonding_curve_token_account uses associated_token::mint and associated_token::authority, so the TokenAccount can be created in advance. If this already exists, creating the function will fail because init is used. An attacker can extract the calculated bonding_curve address and create a TokenAccount to prevent users from creating a Bonding Curve.

## Recommendation
```solidity
#[account(
    init_if_needed,
    payer = creator,
    associated_token::mint = mint,
    associated_token::authority = bonding_curve,
)]
pub bonding_curve_token_account: Box<Account<'info, TokenAccount>>,
```
