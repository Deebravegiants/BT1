# [M] Assumption that all tokens have 18 decimals will lead to wrong calculations

## Summary
Severity: Medium
Contest weight: 0.4245
Dataset id: 15757
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are functions related to calculating rewards that assumes all tokens involved have 18 decimals. Such functions are rewardsPerToken and earned inside CommunalFarm:  
```solidity
function rewardsPerToken() public view returns (uint256[] memory newRewardsPerTokenStored) {
} else {
    newRewardsPerTokenStored = new uint256[](rewardTokens.length);
    for (uint256 i = 0; i < rewardsPerTokenStored.length; i++) {
        newRewardsPerTokenStored[i] = rewardsPerTokenStored[i].add(
            lastTimeRewardApplicable().sub(lastUpdateTime).mul(rewardRates[i]).mul(1e18).div(_total_combined_weight) //@audit mul(1e18) assumes all tokens have 18 decimals
        );
    }
}
...
function earned(address account) public view returns (uint256[] memory new_earned) {
    for (uint256 i = 0; i < rewardTokens.length; i++) {
        new_earned[i] = (_combined_weights[account])
            .mul(reward_arr[i].sub(userRewardsPerTokenPaid[account][i]))
            .div(1e18)
            .add(rewards[account][i]);
    }
}
```  
This is problematic because the protocol intends to use USDC and USDT tokens but they both have 6 decimals. This leads to wrong reward calculations and effectively loss of funds for all pools that will be using tokens with different decimals than 18.

## Recommendation
Add support for different number of decimals than 18 by dynamically checking decimals() for the tokens that are part of the rewards calculations.  
SumerMoney_report.md
