# [H] `executeIsolateLiquidate

## Summary
Severity: High
Contest weight: 0.7968
Dataset id: 22311
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Code reference: [IsolateLogic.sol#L499](https://github.com/code-423n4/2024-12-benddao/blob/489f8dd0f8e86e5a7550cc6b81f9edfe79efbf4e/src/libraries/logic/IsolateLogic.sol#L499)

When `executeIsolateLiquidate()` is executed, it will account `totalBidAmout/availableLiquidity`.

The main accounting code is as follows:

```solidity
function executeIsolateLiquidate(InputTypes.ExecuteIsolateLiquidateParams memory params) internal {
    ...

    InterestLogic.updateInterestRates(poolData, debtAssetData, vars.totalBorrowAmount, 0);

    if (vars.totalExtraAmount > 0) {
        // transfer underlying asset from caller to pool
        VaultLogic.erc20TransferInLiquidity(debtAssetData, params.msgSender, vars.totalExtraAmount);
    }

    // bid already in pool and now repay the borrow but need to increase liquidity
    VaultLogic.erc20TransferOutBidAmountToLiqudity(debtAssetData, vars.totalBorrowAmount);

    // transfer erc721 to winning bidder
    if (params.supplyAsCollateral) {
        VaultLogic.erc721TransferIsolateSupplyOnLiquidate(
            nftAssetData,
            vars.winningBidder,
            params.nftTokenIds,
            true
        );
    } else {
        VaultLogic.erc721DecreaseIsolateSupplyOnLiquidate(nftAssetData, params.nftTokenIds);

        VaultLogic.erc721TransferOutLiquidity(nftAssetData, vars.winningBidder, params.nftTokenIds);
    }
}

function erc20TransferInLiquidity(DataTypes.AssetData storage assetData, address from, uint256 amount) internal {
    address asset = assetData.underlyingAsset;
    uint256 poolSizeBefore = IERC20Upgradeable(asset).balanceOf(address(this));

    assetData.availableLiquidity += amount;

    IERC20Upgradeable(asset).safeTransferFrom(from, address(this), amount);

    uint256 poolSizeAfter = IERC20Upgradeable(asset).balanceOf(address(this));
    require(poolSizeAfter == (poolSizeBefore + amount), Errors.INVALID_TRANSFER_AMOUNT);
}

function erc20TransferOutBidAmountToLiqudity(DataTypes.AssetData storage assetData, uint amount) internal {
    require(assetData.totalBidAmout >= amount, Errors.ASSET_INSUFFICIENT_BIDAMOUNT);
    assetData.totalBidAmout -= amount;

    assetData.availableLiquidity += amount;
}
```

We know from the above code that the current formula is as follows:

1. availableLiquidity += (totalBorrowAmount + totalExtraAmount)
2. totalBidAmout -= totalBorrowAmount

Both of these accounting errors. TotalExtraAmount is calculated twice.totalBorrowAmount already contains totalExtraAmount.

Example:  
Suppose: total Borrow Amount = 100 , Actual Bid Amout = 80  
So: total Extra Amount = 20

but in the current algorithm:

1. availableLiquidity += (totalBorrowAmount + totalExtraAmount) = 100 + 20 = 120
2. totalBidAmout -= totalBorrowAmount = 100

The correct value is:

1. availableLiquidity += totalBorrowAmount = 100
2. totalBidAmout -= (totalBorrowAmount - totalExtraAmount) = (100 - 20) = 80

## Recommendation
```solidity
function executeIsolateLiquidate(InputTypes.ExecuteIsolateLiquidateParams memory params) internal {
    ...

    InterestLogic.updateInterestRates(poolData, debtAssetData, vars.totalBorrowAmount, 0);

    if (vars.totalExtraAmount > 0) {
        // transfer underlying asset from caller to pool
        VaultLogic.erc20TransferInLiquidity(debtAssetData, params.msgSender, vars.totalExtraAmount);
    }

    // bid already in pool and now repay the borrow but need to increase liquidity
-   VaultLogic.erc20TransferOutBidAmountToLiqudity(debtAssetData, vars.totalBorrowAmount);
+   VaultLogic.erc20TransferOutBidAmountToLiqudity(debtAssetData, vars.totalBorrowAmount - vars.totalExtraAmount );
```

> Fixed in [commit 18a4b84](https://github.com/BendDAO/bend-v2/commit/18a4b84b51d2381e60e5c2ca9053186f9ca41637)
