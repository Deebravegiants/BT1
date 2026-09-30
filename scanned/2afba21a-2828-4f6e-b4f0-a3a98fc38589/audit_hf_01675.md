# [M] Staking will get permanently DoS'ed if their total_staked goes down heavily and round finished

## Summary
Severity: Medium
Contest weight: 0.6747
Dataset id: 9062
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
pub fn handle_deposit_reward_token(ctx: Context<DepositRewardToken>, amount: u64) ->
Result<()> {
    ...
    require!(
    staking_state.total_staked as u128 >= base,
    CustomError::InsufficientStake
    );
    ...
}
```
For users to stake, we are preventing new stakers to stake, if the Round finished.
```solidity
pub fn handle_stake(ctx: Context<Stake>, amount: u64) -> Result<()> {
    ...
    // Don't allow staking when there is no time remaining after the first rewards have been deposited.  
    if end_staking_period != 0 {
        let time_remaining = end_staking_period
        .checked_sub(current_time)
        .ok_or(CustomError::TimeUnderflow)?;
        require!(time_remaining > 0, CustomError::StakingEnded);
    }
    ...
}
```
- No one can stake after the staking round finish
- The new round only starts after depositing tokens calling handle_deposit_reward_token
- handle_deposit_reward_token will not accept depositing tokens if total_staked is less than base (1 token unit)
- If at a given round a lot of stakers unstaked and total_staked goes below base (1 token unit), and round finished. The Protocol will get permanently DoS'ed
- No one can stake, admins can't deposit tokens, the Staking will be stopped forever.

## Recommendation
Modify The check to only be for the first round only, if the round is not the first, don't enforce the check.
```solidity
pub fn handle_deposit_reward_token(ctx: Context<DepositRewardToken>, amount: u64) ->
Result<()> {
    ...
    require!(
    -       staking_state.total_staked as u128 >= base,
    +       staking_state.total_staked as u128 >= base || staking_state.end_staking_period > 0,
    CustomError::InsufficientStake
    );
    ...
}
```
