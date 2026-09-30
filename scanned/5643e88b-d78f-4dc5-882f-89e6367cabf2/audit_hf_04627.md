# [M] The calculation of `assetsMax` is incorrect.

## Summary
Severity: Medium
Contest weight: 0.6356
Dataset id: 22305
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
In the `_undeploy` function, `assetsMax` is incorrectly calculated because the contract directly retrieves `totalSupplyAssets` and `totalSupplyShares` from `_morpho` storage without accounting for the accrued interest over time. This leads to an underestimation of `assetsMax`, which may allow users to withdraw more assets than they should, causing losses to other users.
```

## Proof of Concept
```solidity
/// @notice Retrieves the current balance of the managed asset in the Morpho protocol.
/// @return The current balance of the managed asset.
function _getBalance() internal view override returns (uint256) {
    return _morpho.expectedSupplyAssets(_marketParams, address(this));
}

In the StrategySupplyMorpho contract, when retrieving assets, the `expectedSupplyAssets` function is used, which considers accrued interest and fees from the elapsed time since the last update. This ensures that the withdraw and redeem functions calculate assets, including unaccounted interest.

function _undeploy(uint256 amount) internal override returns (uint256) {
    Id id = _marketParams.id();
    uint256 assetsWithdrawn = 0;
    uint256 totalSupplyAssets = _morpho.totalSupplyAssets(id);
    uint256 totalSupplyShares = _morpho.totalSupplyShares(id);

    uint256 shares = _morpho.supplyShares(id, address(this));
    uint256 assetsMax = shares.toAssetsDown(totalSupplyAssets, totalSupplyShares);

    if (amount >= assetsMax) {
        (assetsWithdrawn, ) = _morpho.withdraw(_marketParams, 0, shares, address(this), address(this));
    } else {
        (assetsWithdrawn, ) = _morpho.withdraw(_marketParams, amount, 0, address(this), address(this));
    }

    return assetsWithdrawn;
}

However, in the `_undeploy` function, the calculation of `assetsMax` does not account for the accrued interest and fees over time. This may result in `assetsMax` being underestimated compared to its actual value. On the other hand, the `amount` parameter includes accrued interest and fees, which can lead to the function entering the wrong branch. If the function mistakenly enters the second branch, it may incorrectly convert all _morpho shares in the strategy to assets and send them to the withdrawer. In this case, the strategy’s assets will be 0, but the vault shares will still remain in the vault. The remaining shareholders in the vault will not be able to normally claim assets.

Example: 

1. **Initial Deposits**:  
`user1` deposits `1e16` assets into the vault and receives `1e16` shares. `user2` deposits `1e20` assets and receives `1e20` shares. 
2. **Interest Accumulation**:  
After some time, the `_morpho` strategy generates interest. The vault’s `totalAssets()` now returns `1e20 + 1e16 + 1e17` assets. 
3. **Redeem by user2**:  
`user2` decides to redeem all their shares. When calculating `withdrawAmount = (shares * totalAssets()) / totalSupply()`, `totalAssets()` includes the interest. The calculated `withdrawAmount` is passed to the `_undeploy` function. In `_undeploy`, the maximum amount of assets that can be converted from the current `_morpho` shares (`assetsMax`) is calculated. However, since the calculation of `assetsMax` does not account for the interest, `assetsMax < withdrawAmount`. 

As a result, the strategy withdraws all `_morpho` shares, converts them into assets, and sends them to `user2`. This means `user2` inadvertently receives both their own principal and interest as well as `user1`’s principal and interest. 

4. **Abnormal State**:  
Now, the strategy holds no `_morpho` shares, so `totalAssets()` returns `0`. However, the vault still has `user1`’s `1e16` shares. This creates an abnormal state in the vault.
```

## Recommendation
No recommendation
