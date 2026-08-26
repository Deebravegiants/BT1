# [M] Improper escrow configuration can lead to loss of Rewards

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/63
Type: sherlock-finding

## Details
bin2chen

medium

# Improper escrow configuration can lead to loss of Rewards

## Summary
No restrictions "escrowPortion!=0" and _escrowPool==address(0), which can lead to lost rewards.

## Vulnerability Detail
At claimRewards(), if  "escrowPortion" configured, will calculates escrowedRewardAmount to escrowPool, but when escrowPool==address(0), it does not do, resulting in if escrowPortion!==0 and escrowPool=address(0), that rewards will be lost.
```solidity
    function __BasePool_init(
        string memory _name,
        string memory _symbol,
        address _depositToken,
        address _rewardToken,
        address _escrowPool,
        uint256 _escrowPortion,
        uint256 _escrowDuration
    ) internal onlyInitializing {
        ....
        escrowPool = ITimeLockPool(_escrowPool); /**** when escrowPortion!=0 escrowPool can be address(0)****/
        escrowPortion = _escrowPortion;  
    }
```
```solidity
    function claimRewards(address _receiver) external {
        uint256 escrowedRewardAmount = rewardAmount * escrowPortion / 1e18;
        /*** when escrowPortion!=0 and address(escrowPool) == address(0) will lost escrowedRewardAmount****/
        if(escrowedRewardAmount != 0 && address(escrowPool) != address(0)) {
            escrowPool.deposit(escrowedRewardAmount, escrowDuration, _receiver);   /*** don't execute***/
        }

        // ignore dust
        if(nonEscrowedRewardAmount > 1) {
            rewardToken.safeTransfer(_receiver, nonEscrowedRewardAmount);
        }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/63_
