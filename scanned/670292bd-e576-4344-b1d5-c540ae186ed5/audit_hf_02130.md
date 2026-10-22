# [H] Exposure Of Permissioned VaultFarm::massUpdatePools()

## Summary
Severity: High
Contest weight: 0.5928
Dataset id: 11961
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Duet Bond feature has the VaultFarm contract to farm the Epoch tokens for vault users. When examining the implementation of the VaultFarm contract, we notice the presence of a specific routine, i.e., massUpdatePools(). As the name indicates, this routine is used to update reward variables for all pools with the given input parameters. To elaborate, we show below the code snippet of this function.
```solidity
function massUpdatePools(address[] memory epochs , uint256[] memory rewards) public {
    uint256 poolLen = pools.length;
    uint256 epochLen = epochs.length;
    uint[] memory epochArr = new uint[](epochLen);
    for (uint256 pi = 0; pi < poolLen; pi++) {
        for (uint256 ei = 0; ei < epochLen; ei++) {
            epochArr[ei] = rewards[ei] * allocPoint[pools[pi]] / totalAllocPoint;
        }
        Pool(pools[pi]).updateReward(epochs , epochArr , periodFinish);
    }
    epochRewards = rewards;
    lastUpdateSecond = block.timestamp;
}
```
However, we notice that this routine is currently permissionless, which means it can be invoked by anyone to update reward variables for all pools according to his wish. To fix, the function type needs to be changed from public to internal such that this function can only be accessed internally.

## Recommendation
Adjust the function type from public to internal for the above massUpdatePools() function.
