# [H] `_liquidateUser` uses same minAssetAmount for multiple borrowers leading to DoS or loss

## Summary
Severity: High
Contest weight: 0.6844
Dataset id: 19071
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Singularity and BigBang, the `minAssetAmount` in `_liquidateUser()` is provided by the liquidator as a slippage protection to ensure that the swap provides the specified `amountOut`. However, the same value is utilized even when `liquidate()` is used to liquidate multiple borrowers.

```solidity
function _liquidateUser(
    ...
    uint256 minAssetAmount = 0;
    if (dexData.length > 0) {
        // @audit the same minAssetAmount is incorrectly applied to all liquidations
        minAssetAmount = abi.decode(dexData, (uint256));
    }

    ISwapper.SwapData memory swapData = swapper.buildSwapData(
        collateralId,
        assetId,
        0,
        collateralShare,
        true,
        true
    );
    swapper.swap(swapData, minAssetAmount, address(this), "");
```

Using the same `minAssetAmount` (minimum amountOut for swap) for the liquidation of multiple borrowers will result in inaccurate slippage protection and transaction failure.

If `minAssetAmount` is too low, there will be insufficient slippage protection and the liquidator and protocol could be short changed with a worse than expected swap.

If `minAssetAmount` is too high, the liquidation will fail as the swap will not be successful.

## Proof of Concept
**First scenario**

1. Liquidator liquidates two loans X & Y using `liquidate()`, and set the `minAssetAmount` to be 1000 USDO.
2. Loan X liquidated collateral is worth 1000 USDO and the swap is completely successful with zero slippage.
3. However, Loan Y liquidated collateral is worth 5000 USDO, but due to low liquidity in the swap pool, it was swapped at 1000 USDO (`minAssetAmount`).

The result is that the liquidator will receive a fraction of the expected reward and the protocol gets repaid at 1/5 of the price, suffering a loss from the swap.

**Second scenario**

1. Liquidator liquidates two loans X & Y using `liquidate()`, and set the `minAssetAmount` to be 1000 USDO.
2. Loan X liquidated collateral is worth 1000 USDO and the swap is completely successful with zero slippage.
3. We suppose Loan Y’s liquidated collateral is worth 300 USDO.

Now the `minAssetAmount` of 1000 USDO will be higher than the collateral, which is unlikely to be completed as it is higher than market price. That will revert the entire `liquidate()`, causing the liquidation of Loan X to fail as well.

## Recommendation
Update `liquidate()` to allow liquidator to pass in an array of `minAssetAmount` values that corresponds to the liquidated borrower.

An alternative, is to pass in the minimum expected price of the collateral and use that to compute the `minAssetAmount`.
