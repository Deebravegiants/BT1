# [H] Revisited Logic Of Staking::clearUserDepositTime()

## Summary
Severity: High
Contest weight: 0.6164
Dataset id: 12364
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function getAirdrop() external {
    UserInfo memory userInfo = IStaking(poolAddress).getUserInfo(msg.sender);
    require(userInfo.depositTime > 0, "error");
    uint diff = block.timestamp - userInfo.depositTime;
    IStaking(poolAddress).clearUserDepositTime(msg.sender);
}

function clearUserDepositTime(address user) public {
    require(msg.sender == airdropContract, "can't clear");
    UserInfo memory result = userInfo[user];
    result.depositTime = 0;
}
```
The Staking contract is one of the main entries for interaction with users, which provides an incentive mechanism that rewards the deposits of the supported stakeToken token with the rewardToken token. Meanwhile, an airdrop mechanism is introduced to reward the depositors who meet the following two criteria: the lockup period of the deposit is larger than the specified period in the airdrop contract and the deposit amount is larger than the specified threshold in the Staking contract. In particular, the clearUserDepositTime() routine is designed to reset the user's deposit time when the user claims the airdrop reward. While examining its logic, we notice there is an improper implementation that needs to be improved. To elaborate, we show below the related code snippet of the contracts. The clearUserDepositTime() routine is called (line 37) inside the getAirdrop() routine to reset the user's deposit time. However, in the clearUserDepositTime() routine, we notice the result variable is defined as memory rather than storage (line 420), which will result in the failure of the deposit time reset. With that, the depositor has capability to claim the airdrop reward repeatedly.

## Recommendation
Correct the implementation of the above-mentioned routine.
