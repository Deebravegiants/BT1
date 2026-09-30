# [M] DAO unable to withdraw their funds due to

## Summary
Severity: Medium
Contest weight: 0.5696
Dataset id: 22702
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Convex admin action can lead to the fund of Zivoe protocol and its users being stuck, resulting in DAO being unable to push/pull assets from convex_lockers. considered "RESTRICTED". This means that any issue related to Convex‘s admin action that could negatively affect Zivoe protocol/users will be considered valid in Q: Are the admins of the protocols your contracts integrate with (if any) TRUSTED or RESTRICTED? RESTRICTED In current BaseRewardPool.sol used by convex, admin can add infinite extraRewards:
```solidity
function extraRewardsLength() external view returns (uint256) {
    return extraRewards.length;
}

function addExtraReward(address _reward) external returns(bool){
    require(msg.sender == rewardManager, "!authorized");
    require(_reward != address(0), "!reward setting");
    extraRewards.push(_reward);
    return true;
}
```
By setting a malicious token or add a lot of tokens, it is easy to completely forbid Zivoe DAO to pullFromLocker, since claimRewards() is forced to call:
```solidity
function pullFromLocker(address asset, bytes calldata data) external override onlyOwner {
    require(asset == convexPoolToken, "OCY_Convex_C::pullFromLocker() asset != convexPoolToken");
    claimRewards(false);
    ...
```
The fund of Zivoe protocol and its users will be stuck, resulting in users being unable to withdraw their assets.

## Recommendation
and develop a contingency plan to manage it.
