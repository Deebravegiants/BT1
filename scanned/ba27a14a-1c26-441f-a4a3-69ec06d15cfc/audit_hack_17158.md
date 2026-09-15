# [H] Potential loss of tokens in SdtBuffer.pullRewards

## Summary
Severity: High
Reporter: Polite Berry Chipmunk
Source: https://github.com/sherlock-audit/2023-11-convergence/blob/main/sherlock-cvg/contracts/Rewards/StakeDAO/SdtBuffer.sol#L132
Type: audit-issue

## Details
# Potential loss of tokens in SdtBuffer.pullRewards

## Summary
Potential loss of tokens in `SdtBuffer.pullRewards`

## Vulnerability Detail
`sdtRewardReceiver` can be zero address inside `CvgControlTower.sol` .

In such case, `SdtBuffer.pullRewards` may transfer tokens to address 0.

https://github.com/sherlock-audit/2023-11-convergence/blob/main/sherlock-cvg/contracts/Rewards/StakeDAO/SdtBuffer.sol#L132

## Impact
Loss of tokens

## Code Snippet

## Tool used

Manual Review

## Recommendation
Check `sdtRewardReceiver` is not zero address

```solidity
        address sdtRewardsReceiver = cvgControlTower.sdtRewardReceiver();
        require(sdtRewardsReceiver != address(0));
```
