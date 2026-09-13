# [M] Lack of Validation:

## Summary
Severity: Medium
Reporter: Brilliant Burlap Ant
Source: https://github.com/sherlock-audit/2024-01-telcoin/blob/main/telcoin-audit/contracts/telx/abstract/RewardsDistributionRecipient.sol#L42
Type: audit-issue

## Details
# Lack of Validation:

## Summary
Lack of Validation: When setting the rewardsDistribution address, there is no check to ensure that the address is a contract and not a regular externally owned account (EOA). This could lead to errors if an EOA is mistakenly set as the rewardsDistribution.

## Vulnerability Detail
 function setRewardsDistribution(
        address rewardsDistribution_
    ) external onlyOwner {
        rewardsDistribution = rewardsDistribution_;
        emit RewardsDistributionUpdated(rewardsDistribution);
    }

## Impact
there is no check to ensure that the address is a contract and not a regular externally owned account (EOA). This could lead to errors if an EOA is mistakenly set as the rewardsDistribution.

## Code Snippet
https://github.com/sherlock-audit/2024-01-telcoin/blob/main/telcoin-audit/contracts/telx/abstract/RewardsDistributionRecipient.sol#L42
## Tool used

Manual Review

## Recommendation
