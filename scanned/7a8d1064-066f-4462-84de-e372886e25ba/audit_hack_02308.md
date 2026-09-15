# [M] \[M04\] Trapped Liquidity Rewards

## Summary
Severity: Medium
Source: https://github.com/OriginProtocol/origin-dollar/blob/bf4ff28d5944ecc277e66294fd2c702fee5cd58b/contracts/contracts/liquidity/LiquidityReward.sol#L114-L118
Type: audit-issue

## Details
Whenever a liquidity reward campaign is initiated, the `LiquidityReward` contract [ensures the contract is preloaded](https://github.com/OriginProtocol/origin-dollar/blob/bf4ff28d5944ecc277e66294fd2c702fee5cd58b/contracts/contracts/liquidity/LiquidityReward.sol#L114-L118) with enough reward tokens to execute the campaign. However, some of these rewards would not be distributed if the [campaign is stopped](https://github.com/OriginProtocol/origin-dollar/blob/bf4ff28d5944ecc277e66294fd2c702fee5cd58b/contracts/contracts/liquidity/LiquidityReward.sol#L137). In this scenario, the excess reward tokens cannot be retrieved from the contract. It would be possible to start a new campaign, but then the funds would be distributed to the existing depositors, which may not be desired (and likely undermines the reason for stopping the campaign). Consider introducing a mechanism to retrieve reward tokens that are not intended for distribution.

**Update:** _Fixed in [PR#688](https://github.com/OriginProtocol/origin-dollar/pull/688)._
