# [M] Timely massUpdatePools During Cake Rate Changes

## Summary
Severity: Medium
Contest weight: 0.6975
Dataset id: 12667
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MasterChefV2 protocol provides an incentive mechanism that rewards the staking of supported assets with the CAKE token. The CAKE rewards are earned from the MasterChef V1 (MCV1) by depositing a dummy token into MCV1. The rewards are carried out by designating a number of staking pools into which supported assets can be staked. The pools are classiﬁed to two diﬀerent pool types (general and special) each of which takes diﬀerent CAKE rate from the total CAKE rewards. And staking users are rewarded in proportional to their share of LP tokens in the reward pool. The CAKE rates of diﬀerent pool types can be dynamically changed via updateCakeRate(). When analyzing the CAKE rates update, we notice the need of timely invoking massUpdatePools() to update the reward distribution before the new CAKE rate becomes eﬀective.

```solidity
function updateCakeRate(
    uint256 _burnRate,
    uint256 _regularFarmRate,
    uint256 _specialFarmRate,
    bool _withUpdate
) external onlyOwner {
    require(_burnRate > 0 && _regularFarmRate > 0 && _specialFarmRate > 0, "MasterChefV2: Cake rate must be greater than 0");
    require(_burnRate.add(_regularFarmRate).add(_specialFarmRate) == CAKE_RATE_TOTAL_PRECISION, "MasterChefV2: Total rate must be 1e12");
    if (_withUpdate)
        massUpdatePools();
    // burn cake base on old burn cake rate
    burnCake(false);
    cakeRateToBurn = _burnRate;
    cakeRateToRegularFarm = _regularFarmRate;
    cakeRateToSpecialFarm = _specialFarmRate;
    emit UpdateCakeRate(_burnRate, _regularFarmRate, _specialFarmRate);
}
```

Similarly, the reward pools can be dynamically added via add() and the weights of supported pools can be adjusted via set(). There is also the need of timely invoking massUpdatePools() to update the reward distribution before the new pool weight becomes eﬀective.

```solidity
function set(
    uint256 _pid,
    uint256 _allocPoint,
    bool _withUpdate
) external onlyOwner {
    // No matter _withUpdate is true or false, we need to execute updatePool once before set the pool parameters.
    updatePool(_pid);
    if (_withUpdate)
        massUpdatePools();
    if (poolInfo[_pid].isRegular)
        totalRegularAllocPoint = totalRegularAllocPoint.sub(poolInfo[_pid].allocPoint).add(_allocPoint);
    else
        totalSpecialAllocPoint = totalSpecialAllocPoint.sub(poolInfo[_pid].allocPoint).add(_allocPoint);
    poolInfo[_pid].allocPoint = _allocPoint;
    emit SetPool(_pid, _allocPoint);
}
```

If the call to massUpdatePools() is not immediately invoked before updating the CAKE rates or the pool weights, certain situations may be crafted to create an unfair reward distribution. Moreover, a hidden pool without any weight can suddenly surface to claim unreasonable share of rewarded tokens. Fortunately, these interfaces are restricted to the owner (via the onlyOwner modiﬁer), which greatly alleviates the concern.

## Recommendation
Timely invoke massUpdatePools() when either any CAKE rate or any pool weight has been updated. In fact, the _withUpdate parameter to the set(), add() and updateCakeRate() routines can be simply ignored or removed.

```solidity
function set(
    uint256 _pid,
    uint256 _allocPoint
) external onlyOwner {
    // No matter _withUpdate is true or false, we need to execute updatePool once before set the pool parameters.
    massUpdatePools();
    if (poolInfo[_pid].isRegular)
        totalRegularAllocPoint = totalRegularAllocPoint.sub(poolInfo[_pid].allocPoint).add(_allocPoint);
    else
        totalSpecialAllocPoint = totalSpecialAllocPoint.sub(poolInfo[_pid].allocPoint).add(_allocPoint);
    poolInfo[_pid].allocPoint = _allocPoint;
    emit SetPool(_pid, _allocPoint);
}
```
