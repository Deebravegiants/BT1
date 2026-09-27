# [M] StakingRewardsManager:recoverERC20FromStaking allow SUPPORT_ROLE retrieve rewardsToken

## Summary
Severity: Medium
Reporter: Dazzling Plastic Barracuda
Source: https://github.com/sherlock-audit/2024-01-telcoin/blob/main/telcoin-audit/contracts/telx/core/StakingRewardsManager.sol#L216-L224
Type: audit-issue

## Details
# StakingRewardsManager:recoverERC20FromStaking allow SUPPORT_ROLE retrieve rewardsToken

## Summary
which allows the owner SUPPORT_ROLE privilege,  to retrieve the rewards tokens, perhaps as a way to rug depositors
## Vulnerability Detail
The recoverERC20FromStaking function in the StakingRewardsManager allows the owner to retrieve ERC20 tokens from a StakingRewards contract.
## Impact
medium，rug rewardsToken
## Code Snippet
https://github.com/sherlock-audit/2024-01-telcoin/blob/main/telcoin-audit/contracts/telx/core/StakingRewardsManager.sol#L216-L224
## Tool used

Manual Review

## Recommendation
1.        require(
            tokenAddress != address(staking.rewardsToken),
            "Cannot withdraw the rewards token"
        );
2. emit ERC20RecoveredFromStaking(token, msg.sender, amount);
