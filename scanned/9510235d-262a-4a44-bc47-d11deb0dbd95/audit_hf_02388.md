# [H] Nonfunctional _onlyWhiteListed Modifier in MasterRadpie

## Summary
Severity: High
Contest weight: 0.6112
Dataset id: 12876
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Radpie protocol has a keyMasterRadpie contract to manage all reward pools. In particular, each reward pool may be updated with an admin routine, i.e., updatePoolsAlloc(). Our analysis shows that this admin routine has a flawed modifier that needs to be fixed. To elaborate, we show below the related code snippet from the updatePoolsAlloc() routine as well as this specific _onlyWhiteListed modifier. Our analysis shows that the modifier does not work as expected. Specifily, if the caller is indeed authorized to update the allocation of reward pools, the function body will be simply skipped. In other words, there is no admin routine to update the allocation of current reward pools. Fortunately, it does not result in any fund loss.
```solidity
function updatePoolsAlloc(
    address[] calldata _stakingTokens,
    uint256[] calldata _allocPoints
) external _onlyWhiteListed {
    massUpdatePools();
    if (_stakingTokens.length != _allocPoints.length) revert LengthMismatch();
    for (uint256 i = 0; i < _stakingTokens.length; i++) {
        uint256 oldAllocPoint = tokenToPoolInfo[_stakingTokens[i]].allocPoint;
        totalAllocPoint = totalAllocPoint - oldAllocPoint + _allocPoints[i];
        tokenToPoolInfo[_stakingTokens[i]].allocPoint = _allocPoints[i];
        emit UpdatePoolAlloc(_stakingTokens[i], oldAllocPoint, _allocPoints[i]);
    }
}

modifier _onlyWhiteListed() {
    if (AllocationManagers[msg.sender]) return;
    if (PoolManagers[msg.sender]) return;
    if (msg.sender == owner()) return;
    revert OnlyWhiteListedAllocaUpdator();
}
```

## Recommendation
Revise the above logic to properly update the allocation of current reward pools.
