# [H] LPS-1 | Rewards May Be Stolen

## Summary
Severity: High
Contest weight: 0.1659
Dataset id: 9323
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The uniswapV3Staker contract which the LPStaker interacts with allows any arbitrary address to directly call the unstakeToken function and unstake for any depositor after the incentive key endTime. When a deposit is unstaked from an incentive key directly from the uniswapV3Staker, those rewards will be incremented for the LPStaker contract, but not credited towards the user who staked. Therefore malicious stakers may unstake for other stakers and immediately claim their rewards as their own by unstaking through the LPStaker contract.

## Recommendation
Consider using a modified version of the uniswapV3Staker where the depositor must always be the one to unstake. Otherwise be sure to manage the incentive keys extremely carefully and never allow an incentive key to reach its endTime while users have staked for it.
