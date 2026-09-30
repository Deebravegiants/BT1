# [M] Timely accumulateReward() in MasterChefV3::onERC721Received()

## Summary
Severity: Medium
Contest weight: 0.4598
Dataset id: 12665
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MasterChefV3 contract provides an incentive mechanism that rewards the staking of the supported Pancake V3 Positions NFT-V1 with the CAKE token. The rewards are carried out by designating a number of staking pools into which supported Pancake V3 Positions NFT-V1 can be staked. Specially, the user can stake the supported Pancake V3 Positions NFT-V1 into the MasterChefV3 contract via ERC721::safeTransferFrom(). Then the MasterChefV3::onERC721Received() routine will be triggered to perform the staking process. While examining its logic, we notice the need of timely invoking LMPool.accumulateReward() to update the accumulated reward per share before the UserPositionInfo of the _tokenId (lines 354 - 356) is updated. Otherwise, the user may gain unexpected CAKE as reward.

```solidity
function onERC721Received(address, address _from, uint256 _tokenId, bytes calldata) external returns (bytes4) {
    if (msg.sender != address(nonfungiblePositionManager)) revert NotPancakeNFT();
    DepositCache memory cache;
    (
        cache.token0,
        cache.token1,
        cache.fee,
        cache.tickLower,
        cache.tickUpper,
        cache.liquidity
    ) = nonfungiblePositionManager.positions(_tokenId);
    if (cache.liquidity == 0) revert NoLiquidity();
    uint256 pid = v3PoolPid[cache.token0][cache.token1][cache.fee];
    if (pid == 0) revert InvalidNFT();
    PoolInfo memory pool = poolInfo[pid];
    ILMPool LMPool = ILMPool(pool.v3Pool.lmPool());
    if (address(LMPool) == address(0)) revert NoLMPool();
    UserPositionInfo storage positionInfo = userPositionInfos[_tokenId];
    positionInfo.tickLower = cache.tickLower;
    positionInfo.tickUpper = cache.tickUpper;
    positionInfo.user = _from;
    positionInfo.pid = pid;
    updateLiquidityOperation(positionInfo, _tokenId, 0);
    positionInfo.rewardGrowthInside = LMPool.getRewardGrowthInside(cache.tickLower, cache.tickUpper);
    // Update Enumerable
    addToken(_from, _tokenId);
    emit Deposit(_from, pid, _tokenId, cache.liquidity, cache.tickLower, cache.tickUpper);
    return this.onERC721Received.selector;
}
```

## Recommendation
Timely invoke accumulateReward() when the supported Pancake V3 Positions NFT-V1 is staked.
