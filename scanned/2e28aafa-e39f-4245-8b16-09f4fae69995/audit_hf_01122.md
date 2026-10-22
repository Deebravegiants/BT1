# [H] Migration Leaves Some Unused assets Locked

## Summary
Severity: High
Reporter: KupiaSec, also found by Aamirusmani1552 and deadrosesxyz
Contest weight: 0.6086
Dataset id: 4593
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Airlock.migrate() function incorrectly computes the migration amounts total0 and total1. Initially, total0 and total1 represent the amounts of tokens retrieved from the Uniswap V3 pool. The function then adds the amount of asset already held in the Airlock contract to total0 or total1, depending on whether the asset corresponds to token0 or token1. However, the calculation of the amount of asset already held in the Airlock contract is flawed. It is miscalculated as assetData.totalSupply - assetData.numTokensToSell, as indicated in lines 241 and 243. This calculation is incorrect because numTokensToSell reflects the approved amount for initialization, not the actual amount utilized during the initialization. As a result, the unused portion of the approved amount during initialization remains locked and is not utilized for migration.
```solidity
function migrate(
    address asset
) external {
    AssetData memory assetData = getAssetData[asset];
    // ...
    if (token0 == asset) {
        total0 += assetData.totalSupply - assetData.numTokensToSell;
    } else {
        total1 += assetData.totalSupply - assetData.numTokensToSell;
    }
    // ...
}

function create(
    // ...
    ERC20(asset).approve(address(createData.poolInitializer), createData.numTokensToSell);
    pool = createData.poolInitializer.initialize(
        asset, createData.numeraire, createData.numTokensToSell, createData.salt,
        createData.poolInitializerData
    );
    // ...
}
```

Impact Explanation:
High. Some assets remain locked.

## Recommendation
Track the exact amount used during initialization.
3.2
