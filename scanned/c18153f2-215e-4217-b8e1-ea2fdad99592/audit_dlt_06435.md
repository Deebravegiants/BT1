# [H] Malicious user can lock  CvxConvergenceLocker cvxcrv reward forever

## Summary
Severity: High
Chain: Smart contract
Component: Convergence---Convex-integration
Published: 2024-05-02
Source: https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/issues/40
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xa3489d293b99d9cca75b5267d9e7accdf3fb5aa220f43f086fd971a55c85c87a
**Severity:** high

**Description:**
**Description**\

After user mint token in CvxConvergenceLocker, anyone can trigger [lock](https://github.com/Cvg-Finance/hats-audit/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/cvgCVX/CvxConvergenceLocker.sol#L112) and the reward starts accuring

when staking position service can call pullRewards to get the reward from the locker contract,

to get the reward, we are calling [CVX_LOCKER.getReward(address(this))](https://github.com/Cvg-Finance/hats-audit/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/cvgCVX/CvxConvergenceLocker.sol#L130)

```solidity
 /// @dev claim rewards
        CVX_LOCKER.getReward(address(this));

        uint256 rewardLength = rewardTokensConfiguration.length;
        address treasuryPod = cvgControlTower.treasuryPod();
        address rewardReceiver = address(cvgControlTower.cvxRewardDistributor());

        ICommonStruct.TokenAmount[] memory cvxRewardAssets = new ICommonStruct.TokenAmount[](rewardLength);
        uint256 counterDelete;

        for (uint256 i; i < rewardLength; ) {
            RewardConfiguration memory rewardConfiguration = rewardTokensConfiguration[i];
            uint256 balance = rewardConfiguration.token.balanceOf(address(this));

```

but if we take a look at the getReward function in CrxLockerV2

https://etherscan.io/address/0x72a19342e8F1838460eBFCCEf09F6585e32db86E#code#L1727

```solidity
   function getReward(address _account, bool _stake) public nonReentrant updateReward(_account) {
        for (uint i; i < rewardTokens.length; i++) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/issues/40_
