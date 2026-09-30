# [M] getStakedAmount can be manipulated

## Summary
Severity: Medium
Contest weight: 0.6867
Dataset id: 2794
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
getStakedAmount returns stakedAmount of Aegis vault within Berachain reward's vault by calling balanceOf.
```solidity
function getStakedAmount(IBerachainRewardsVault rewardsVault) private view returns (uint256 stakedAmount) {
    if (address(rewardsVault) != NULL_ADDRESS) {
        stakedAmount = rewardsVault.balanceOf(address(this));
    }
    /// @dev else stakedAmount defaults to 0
}
```
This function is called by _calculateAegisVaultAmountsInICHIVaultIncludingStaked, which is used in several important getter functions, such as getUserBalance, getDepositPosition, getTargetPosition, and checkUpkeep.
An attacker can manipulate this value by calling delegateStake within the Berachain reward contract and providing a staked balance to Aegis Vault, causing the returned values from those getters to be inaccurate and not using the actual self-staked balance.
```solidity
function delegateStake(address account, uint256 amount) external nonReentrant whenNotPaused {
    _stake(account, amount);
    if (account != msg.sender) {
        unchecked {
            DelegateStake storage info = _delegateStake[account];
            uint256 delegateStakedBefore = info.delegateTotalStaked;
            uint256 delegateStakedAfter = delegateStakedBefore + amount;
            // `<=` and `<` are equivalent here but the former is cheaper
            (delegateStakedAfter <= delegateStakedBefore) DelegateStakedOverflow.selector.revertWith();
            info.delegateTotalStaked = delegateStakedAfter;
            // if the total staked by all delegates doesn't overflow, the
            // following won't
            info.stakedByDelegate[msg.sender] += amount;
            emit DelegateStaked(account, msg.sender, amount);
        }
    }
}
```

## Recommendation
Modify getStakedAmount as follows:
```solidity
function getStakedAmount(IBerachainRewardsVault rewardsVault) private view returns (uint256 stakedAmount) {
    if (address(rewardsVault) != NULL_ADDRESS) {
        stakedAmount = rewardsVault.balanceOf(address(this)) - rewardsVault.getTotalDelegateStaked(address(this));
    }
    /// @dev else stakedAmount defaults to 0
}
```
