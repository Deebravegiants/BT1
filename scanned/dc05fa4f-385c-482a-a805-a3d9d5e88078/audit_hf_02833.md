# [M] A malicious/compromised owner or TokenManager can rug rewards SumerMoney_report.md

## Summary
Severity: Medium
Contest weight: 0.4349
Dataset id: 15759
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The recoverERC20 functions are intended to allow the owner and the TokenManager to withdraw any mistakenly tokens sent to the system:  
```solidity
onlyTknMgrs(tokenAddress) {
    // Cannot rug the staking / LP tokens
    require(tokenAddress != address(stakingToken), 'Cannot withdraw staking / LP tokens');
    // Check if the desired token is a reward token
    bool isRewardToken = false;
    for (uint256 i = 0; i < rewardTokens.length; i++) {
        if (rewardTokens[i] == tokenAddress) {
            isRewardToken = true;
            break;
        }
    }
    // Only the reward managers can take back their reward tokens
    if (isRewardToken && rewardManagers[tokenAddress] == msg.sender) {
        IERC20(tokenAddress).transfer(msg.sender, tokenAmount);
        emit Recovered(msg.sender, tokenAddress, tokenAmount);
        return;
    }
    // Other tokens, like airdrops or accidental deposits, can be withdrawn by the owner
    else if (!isRewardToken && (msg.sender == owner())) {
        IERC20(tokenAddress).transfer(msg.sender, tokenAmount);
        emit Recovered(msg.sender, tokenAddress, tokenAmount);
        return;
    }
    // If none of the above conditions are true
    else {
        revert('No valid tokens to recover');
    }
}
```  
However, in the instance above which is inside the CommunalFarm contract, the TokenManager can withdraw any amount of the reward tokens without any restrictions. This could lead to a direct theft of all of the reward tokens.

## Recommendation
Consider allowing the privileged roles to be able to withdraw only tokens that are not reward tokens or the stakingToken.
