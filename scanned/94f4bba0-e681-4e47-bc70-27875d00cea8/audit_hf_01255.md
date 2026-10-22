# [C] claim() and unstake() functions will not be useable

## Summary
Severity: Critical
Contest weight: 0.5456
Dataset id: 5767
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The position account in both claim() and unstake() functions is marked with the init constraint, while this same account is already initialized in the stake() function:
```solidity
#[ account(
init,
payer = user,
space = 8 + Position::INIT_SPACE,
) ]
pub position: Box<Account<'info, Position>>,
```
This will cause the claim() and unstake() functions to revert when called, since an account cannot be initialized if it already exists. As a result, all funds staked are stuck indefinitely, as users cannot claim rewards or withdraw their tokens.

## Recommendation
Replace the init constraint with the mut constraint in the position account definition for both claim() and unstake() functions.
