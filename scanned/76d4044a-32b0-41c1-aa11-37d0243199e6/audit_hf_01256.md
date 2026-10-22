# [C] Missing seed and bump constraints in position account in claim() and unstake() functions

## Summary
Severity: Critical
Contest weight: 0.5401
Dataset id: 5768
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The position account in both claim() and unstake() functions is missing seeds and bump constraints, which means a user can include any position account belonging to another user when calling these functions. As a result, a malicious user can claim/unstake others' positions to their own wallet, effectively stealing their funds.
```solidity
#[ account(
init,
payer = user,
space = 8 + Position::INIT_SPACE,
) ]
pub position: Box<Account<'info, Position>>,
```

## Recommendation
Add seeds and bump constraints to the position account in both claim() and unstake() functions, similar to how they are defined in the stake() function.
