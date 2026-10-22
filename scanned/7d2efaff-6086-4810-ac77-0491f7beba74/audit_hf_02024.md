# [M] Improper Logic in Farm::_calcAccOruToAdd()

## Summary
Severity: Medium
Contest weight: 0.4318
Dataset id: 11554
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Orcus protocol has a Farm contract to incentivize the protocol adoption among the community. This Farm follows the popular MasterChef approach to specify the pools for farming. While examining the current logic to calculate the pool-specific accOruPerShare state, we notice the implementation should be improved. In the following, we show the related _calcAccOruToAdd() routine in the Farm contract. As the name indicates, this routine is used to compute the new normalized reward index for the given pool (with the pid). It comes to our attention the computation is scaled by 10**_lpDecimals (line 221), which may cause inconsistency when it does not equal to the intended ORU_PRECISION! In other words, we should use the ORU_PRECISION as the scaling factor, instead of 10**_lpDecimals.
```solidity
/// @dev Calculated amount of accOruPerShare to add to the pool.
function _calcAccOruToAdd(uint256 _pid) internal view returns (uint256) {
    PoolInfo memory pool = poolInfo[_pid];
    uint256 _lpSupply = lpToken[_pid].balanceOf(address(this));
    uint256 _lpDecimals = ERC20(address(lpToken[_pid])).decimals();
    uint64 _currentTs = _currentBlockTs();
    if (_currentTs <= pool.lastRewardTime || _lpSupply <= 0) {
        return 0;
    }
    uint256 _time = _currentTs - pool.lastRewardTime;
    uint256 _oruReward = (_time * oruPerSecond * pool.allocPoint) / totalAllocPoint;
    return (_oruReward * (10**_lpDecimals)) / _lpSupply;
}
```

## Recommendation
Be consistent in the use of the scaling factor for reward index calculation.
