# [H] Business Logic Error in _claimWeekly()

## Summary
Severity: High
Contest weight: 0.7870
Dataset id: 12389
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Legends Never Die, the users can stake their LND tokens into Legend vault and will get BNB-ETH plus BEP20 tokens as rewards. There are two kinds of rewards: weekly rewards and yearly rewards. Weekly rewards are rewards that can be claimed after each week while yearly rewards are rewards that can be claimed after the auction lobby is over. When reviewing the implementation of the MasterVault contract, we notice that the claimWeekly() function has a business logic error which could allow users to claim more rewards than they deserve. In the following, we show the related external function claimWeekly() that is designed to allow the staker to claim the weekly rewards.
```solidity
function claimWeekly(uint256 _vid) external nonReentrant returns (uint256 returnAmount, uint256 rewardAmount) {
    returnAmount = _claim(_vid, _msgSender());
    VaultInfo storage vault = vaultInfo[_vid];
    UserInfo storage user = userInfo[_vid][_msgSender()];
    require(((vault.start < block.number) && (vault.stop < block.number)), "Vault is not started or ended");
    require(!user.claimed, "Tokens already claimed");
    (returnAmount, rewardAmount) = _claimWeekly(vault, user, _vid, _msgSender());
    if (returnAmount > 0) {
        // send tokens to user
        offeringToken.safeTransfer(_msgSender(), returnAmount);
    }
    if (rewardAmount > 0) {
        // send reward tokens to user
        rewardToken.safeTransfer(_msgSender(), rewardAmount);
    }
}
```
The internal function _claimWeekly() (line 362) calculates the amounts of the specified _vid (week) rewards for the msg.sender. However, if the msg.sender did not stake any LND tokens into the Legend vault on this specified _vid, the value of userBalance (lines 385) should take from the previous vault with userBalance greater than 0 instead of from the latest vault into which the msg.sender staked. The reason is that the msg.sender may stake some LND tokens into the Legend vault several weeks after this specified _vid (week) and then claim weekly rewards for this specified _vid. By doing so, the msg.sender can claim more rewards than deserved because the wrong userBalance is used to calculate the rewards share.
```solidity
function _claimWeekly(
    VaultInfo storage vault,
    UserInfo storage user,
    uint256 _vid,
    address _recipient
) internal returns (uint256 returnAmount, uint256 rewardAmount) {
    // calculation how BNB ETH will be sent to user
    uint256 userBalance = user.balance;
    if (userBalance == 0) {
        userBalance = userInfo[stakedInfoUser[_recipient].lastStakeIndex][_recipient].balance;
    }
    uint256 vaultTotalBalance = vault.totalBalanceStored;
    if (vaultTotalBalance == 0) {
        vaultTotalBalance = _getPreviousBalanceStored(_vid);
    }
}
```

## Recommendation
The value of userBalance (lines 385) should take from the previous vault with userBalance greater than 0 instead of from the latest vault which the msg.sender staked into.
