# [M] UpdatedStakerState Account can't be initialized DoSing update_staker_state

## Summary
Severity: Medium
Contest weight: 0.3914
Dataset id: 9063
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
pub struct UpdateStakerState<'info> {
    ...
    #[account(mut)]
    pub updated_staking_state: Account<'info, UpdatedStakerState>,
    pub token_program: Interface<'info, TokenInterface>,
}
```
The problem is that this account can't be initialized in any part in the program. There is no way for users to initialize that account and use it for updating their staking_state.distribution_duration.
The only way for Authors to do this is to deploy a custom program, and create an Account has the same struct, and use it. which is not the normal process especially for normal users who don't know how to deploy programs on Solana and do such a process.

## Recommendation
make the account with init_if_needed, since Same UpdatedStakerState can be used by more than one Author, there is no need to create new one each time. And the seed can be a constant independent to any parameter.
