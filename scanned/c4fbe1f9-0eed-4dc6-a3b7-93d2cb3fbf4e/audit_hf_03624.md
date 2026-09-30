# [H] GMXFuturesPoolHedger's _increasePosition can

## Summary
Severity: High
Contest weight: 0.8013
Dataset id: 19689
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_increasePosition() add to a position no matter how low amount of collateral was obtained from the LiquidityPool.
If the resulting leverage is too high, the new increased position can be liquidated soon and the pool can find itself with no hedge.
If liquidityPool.transferQuoteToHedge(collateralDelta) result is positive, the position increase will carry on, no matter how much funds were obtained from the LiquidityPool.
I.e. zero amount and dust amount of the funds obtained aren't distinct from the hedging position risk perspective, but are treated differently.
More generally, if ‘collateralDelta > liquidityPool.transferQuoteToHedge(collateralDelta)', the resulting leverage needs to be checked before proceeding as it can be too high.
As the market changes constantly the liquidation can realistically happen before any manual collateral adjustment is made. Losing the hedging position due to liquidation will mean that the net option position is now unhedged.
Without hedging the protocol is open to any delta originated losses, which can be massive and can have the net impact up to the protocol insolvency, with net position becoming equivalent to the naked option selling.
There is no prerequisites beside lack of collateral that can take place as a part of usual protocol workflow. There is a massive fund loss impact from the loss of hedging position. Given this setting the severity to be high.
It's now allowed to open a position with any low positive collateral as only collateralDelta == 0 case is reverted:
```solidity
function _increasePosition(
    PositionDetails memory currentPos,
    bool isLong,
    uint sizeDelta,
    uint collateralDelta,
    uint spot
) internal {
    // add margin fee
    // when we increase position, fee always got deducted from collateral
    collateralDelta += _getPositionFee(currentPos.size, sizeDelta, currentPos.entryFundingRate);

    address[] memory path;
    uint acceptableSpot;
    if (isLong) {
        path = new address[](2);
        path[0] = address(quoteAsset);
        path[1] = address(baseAsset);
        acceptableSpot = _convertToGMXPrecision(spot.multiplyDecimal(futuresPoolHedgerParams.acceptableSpotSlippage));
    } else {
        path = new address[](1);
        path[0] = address(quoteAsset);
        acceptableSpot = _convertToGMXPrecision(spot.divideDecimalRound(futuresPoolHedgerParams.acceptableSpotSlippage));
    }
    // if the trade ends up with collateral > size, adjust collateral.
    // gmx restrict position to have size >= collateral, so we cap the collateral to be same as size.
    if (currentPos.collateral + collateralDelta > currentPos.size + sizeDelta) {
        collateralDelta = (currentPos.size + sizeDelta) - currentPos.collateral;
    }
    // if we get less than we want, we will just continue with the same position, but take on more leverage
    collateralDelta = liquidityPool.transferQuoteToHedge(collateralDelta);
    if (collateralDelta == 0) {
        revert NoQuoteReceivedFromLP(address(this));
    }
    // collateralDelta with decimals same as defined in ERC20
    collateralDelta = ConvertDecimals.convertFrom18(collateralDelta, quoteAsset.decimals());
}
```
```solidity
/**
 * @notice Sends quote to the PoolHedger.
 * @dev Transfer amount up to `pendingLiquidity + freeLiquidity`.
 * The hedger must determine what to do with the amount received.
 *
 * @param amount The amount requested by the PoolHedger.
 */
function transferQuoteToHedge(uint amount) external onlyPoolHedger returns (uint) {
    Liquidity memory liquidity = getLiquidity();
    uint available = liquidity.pendingDeltaLiquidity + liquidity.freeLiquidity;
    amount = amount > available ? available : amount;
    _transferQuote(address(poolHedger), amount);
    emit QuoteTransferredToPoolHedger(amount);
    return amount;
}
```

## Recommendation
If the funds available are less than requested there is a choice between under-hedging (not increasing the position) and pushing the leverage too high (increasing it with less collateral than desired).
The preferred option here depends on the resulting leverage. If it is not too high the full position increase is desirable as under-hedging is much more dangerous. But if leverage is being pushed too close to the liquidation threshold, the risk of losing the hedge altogether out-weights the less-then-desired hedging considerations.
This way there is an optimal max leverage parameter that balances these two risks and the decision whether to proceed with that much collateral should be based on the resulting leverage exceeding it or not.
Consider introducing the max leverage parameter or use the global one, say futuresMarketSettings.maxLeverage(marketKey), and reverting the attempts of the hedging position increase that bring the estimated leverage above it.
Such events aren't part of a fully automated workflow and should lead to manual collateral addition and repeating of the hedgeDelta() or updateCollateral() calls.
