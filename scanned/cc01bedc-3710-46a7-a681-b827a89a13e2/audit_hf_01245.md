# [H] DoS in claim Function Due to init Constraint on an Already Initialized Account

## Summary
Severity: High
Contest weight: 0.7459
Dataset id: 5754
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the claim function, the init constraint is incorrectly applied to the PDA position. However, this account is already initialized in the stake function. As a result, the claim function will fail to execute after the initial staking process, leading to a permanent denial of service (DoS) for claiming rewards. This renders the protocol's claiming functionality unusable.
In the claim function, the init constraint is incorrectly applied to the PDA position. However, this account is already initialized in the stake function. As a result, the claim function will fail to execute after the initial staking process, leading to a permanent denial of service (DoS) for claiming rewards. This renders the protocol's claiming functionality unusable.
```solidity
// in claim function
#[ account(
init,
payer = user,
space = 8 + Position::INIT_SPACE,
) ]
pub position: Box<Account<'info, Position>>,
```

## Recommendation
Replace the init constraint with mut to ensure the position account can be modified instead of being reinitialized. Additionally, verify the account’s existence before performing operations to prevent unintended reinitialization attempts.
```solidity
#[ account(mut) ]
```
