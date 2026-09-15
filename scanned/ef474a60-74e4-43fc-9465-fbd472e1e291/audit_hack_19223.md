# [M] No Time Locks or Multi-Sig:

## Summary
Severity: Medium
Reporter: Brilliant Burlap Ant
Source: https://github.com/sherlock-audit/2024-01-telcoin/blob/main/telcoin-audit/contracts/telx/abstract/RewardsDistributionRecipient.sol#L42
Type: audit-issue

## Details
# No Time Locks or Multi-Sig:

## Summary
No Time Locks or Multi-Sig: For high-value contracts, it is often recommended to have time locks or multi-signature requirements for critical operations like changing the rewards distribution address. This contract does not implement such mechanisms.

## Vulnerability Detail
function setRewardsDistribution(
        address rewardsDistribution_
    ) external onlyOwner {
        rewardsDistribution = rewardsDistribution_;
        emit RewardsDistributionUpdated(rewardsDistribution);
    }
## Impact
For high-value contracts, it is often recommended to have time locks or multi-signature requirements for critical operations like changing the rewards distribution address. This contract does not implement such mechanisms.
## Code Snippet
https://github.com/sherlock-audit/2024-01-telcoin/blob/main/telcoin-audit/contracts/telx/abstract/RewardsDistributionRecipient.sol#L42
## Tool used

Manual Review

## Recommendation
