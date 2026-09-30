# [M] Improper Staking Amount In setRewards()

## Summary
Severity: Medium
Contest weight: 0.4594
Dataset id: 11769
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BTC+ protocol has developed a governance subsystem that can reward participating holders. In particular, the governance subsystem is heavily inspired by the Curve DAO implementation and shares the same components, i.e., GaugeController, LiquidityGauge, and VotingEscrow. In the following, we examine a core routine from the LiquidityGauge contract. Speciﬁcally, the routine under examination is setRewards(), which is designed to update the reward contract and reward tokens. This routine is a permissioned one and can only be invoked by the privileged governance for the reward contract update. Its business logic is implemented as follows: it withdraws all staked assets from the current one and then deposits into the new reward contract. It comes to our attention that the deposit into the new reward has an issue in using an incorrect staking amount. Currently, it calculates the staking amount from totalSupply() (line 475), which should be corrected as IERC20Upgradeable(token).balanceOf(this).

```solidity
function setRewards(address _rewardContract, address[] memory _rewardTokens) external onlyGovernance {
    address _currentRewardContract = rewardContract;
    address _token = token;
    if (_currentRewardContract != address(0x0)) {
        _checkpointRewards(address(0x0));
        IUniPool(_currentRewardContract).exit();
        IERC20Upgradeable(_token).safeApprove(_currentRewardContract, 0);
    }
    if (_rewardContract != address(0x0)) {
        require(_rewardTokens.length > 0, "reward tokens not set");
        IERC20Upgradeable(_token).safeApprove(_rewardContract, uint256(int256(1)));
        IUniPool(_rewardContract).stake(totalSupply());
    }
    rewardContract = _rewardContract;
    rewardTokens = _rewardTokens;
    // Complete initial checkpoint to make sure that everything works.
    _checkpointRewards(address(0x0));
    // Reward contract tokenized as well
    unsalvageable[_rewardContract] = true;
    // Don't salvage any reward token
    for (uint256 i = 0; i < _rewardTokens.length; i++) {
        unsalvageable[_rewardTokens[i]] = true;
    }
    emit RewardContractUpdated(_currentRewardContract, _rewardContract, _rewardTokens);
}
```

## Recommendation
Correct the setRewards() logic by calculating the right staking amount.
