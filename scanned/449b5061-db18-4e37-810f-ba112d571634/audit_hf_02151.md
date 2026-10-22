# [H] Proper Share Accounting in emergencyWithdrawNFT()

## Summary
Severity: High
Contest weight: 0.6167
Dataset id: 12053
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.4, the FarmHero protocol provides incentive mechanisms that reward the staking of supported assets with certain reward tokens. The rewards are carried out by designating a number of staking pools into which supported assets can be staked. Each pool has its allocPoint*100%/totalAllocPoint share of scheduled rewards and the rewards for stakers are proportional to their share of LP tokens in the pool. With the NFT support, the protocol provides the emergencyWithdrawNFT() function to allow for emergency NFT withdraws. To elaborate, we show below the full implementation of this function. This function properly transfers out the requested NFTs (line 776), but fails to properly record the internal states, including the user shares, rewardDebt, and gracePeriod (lines 782 784).
```solidity
function emergencyWithdrawNFT(uint256 _pid, uint256[] memory _tokenIds) public isEOA nonReentrant {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][msg.sender];
    require(pool.poolType == PoolType.ERC721, "invalid erc721");
    if (_tokenIds.length > 0) {
        uint256 sharesRemoved = IStrategy(poolInfo[_pid].strat).withdraw(msg.sender, _tokenIds);
        if (sharesRemoved > user.shares) {
            user.shares = 0;
        } else {
            user.shares = user.shares.sub(sharesRemoved);
        }
        for (uint i = 0; i < _tokenIds.length; i++) {
            IERC721(pool.want).transferFrom(address(this), msg.sender, _tokenIds[i]);
        }
    }
    emit EmergencyWithdrawNFT(msg.sender, _pid, _tokenIds);
    user.shares = 0;
    user.rewardDebt = 0;
    user.gracePeriod = 0;
}
```

## Recommendation
Correct the above emergencyWithdrawNFT() function by properly recording the user states.
