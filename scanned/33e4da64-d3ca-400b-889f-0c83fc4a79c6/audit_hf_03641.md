# [M] GMXFuturesPoolHedger's getHedgingLiquidity()

## Summary
Severity: Medium
Contest weight: 0.5927
Dataset id: 19710
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
getHedgingLiquidity() uses theoretical liquidity as a measure of current liquidity conditions, which can be substantially wrong as market moves and hedging position accrues P&L. There is an unaccounted difference between pendingDeltaLiquidity (how much is needed to bring theoretical is and theoretical to-be) and _getCurrentHedgedNetDeltaWithSpot().multiplyDecimal(spotPrice) - _getAllPositionsValue(currentPositions).multiplyDecimal(futuresPoolHedgerParams.targetLeverage) (theoretical and actual now). This difference will emerge if current hedge be replaced with the target one, i.e. current position be closed and one with the target leverage and the current size opened instead. The difference is unrealized P&L and the leverage drift, both from P&L and say leverage parameter changes, if any, i.e. it's a cumulative drift from ideal conditions). With free liquidity calculations being incorrect the hedging possibility control logic will not work as intended. One of the impacts is allowing for positions that cannot be subsequently hedged. Without hedging the protocol is open to any delta originated losses, which can be massive and can have the net impact up to protocol insolvency. There are no material prerequisites. Given the massive fund loss impact from the absence of the hedge setting the severity to be high. The difference between pendingDeltaLiquidity and _getCurrentHedgedNetDeltaWithSpot().multiplyDecimal(spotPrice) - _getAllPositionsValue(currentPositions).multiplyDecimal(futuresPoolHedgerParams.targetLeverage):
oolHedger.sol#L228-L250
```solidity
/**
* @notice Returns pending delta hedge liquidity and used delta hedge liquidity
* @dev include funds potentially transferred to the contract
* @return pendingDeltaLiquidity amount USD needed to hedge. outstanding order is NOT included
* @return usedDeltaLiquidity amount USD already used to hedge. outstanding order is NOT included
*/
function getHedgingLiquidity(
    uint spotPrice
) external view override returns (uint pendingDeltaLiquidity, uint usedDeltaLiquidity) {
    CurrentPositions memory currentPositions = _getPositions();
    usedDeltaLiquidity = _getAllPositionsValue(currentPositions);
    // pass in estimate spot price
    uint absCurrentHedgedDelta =
        Math.abs(_getCurrentHedgedNetDeltaWithSpot(currentPositions, spotPrice));

    uint absExpectedHedge = Math.abs(_getCappedExpectedHedge());
    if (absCurrentHedgedDelta > absExpectedHedge) {
        return (0, usedDeltaLiquidity);
    }
    pendingDeltaLiquidity = (absExpectedHedge -
        absCurrentHedgedDelta).multiplyDecimal(spotPrice).divideDecimal(
        futuresPoolHedgerParams.targetLeverage
    );
}
```
I.e. pendingDelta is not synchronized with the real liquidity situation, making liquidity's pendingDeltaLiquidity biased by the abovementioned difference:
sol#L942-L959
```solidity
function _getLiquidity(
    uint basePrice,
    uint totalPoolValue,
    uint reservedTokenValue,
    uint usedDelta,
    uint pendingDelta,
    uint longScaleFactor
) internal view returns (Liquidity memory) {
    Liquidity memory liquidity = Liquidity(0,0,0,0,0,0,0);
    liquidity.NAV = totalPoolValue;
    liquidity.usedDeltaLiquidity = usedDelta;
    uint usedQuote = totalOutstandingSettlements + totalQueuedDeposits;
    uint totalQuote =
        ConvertDecimals.convertTo18(quoteAsset.balanceOf(address(this)),
            quoteAsset.decimals());

    uint availableQuote = totalQuote > usedQuote ? totalQuote - usedQuote : 0;
    liquidity.pendingDeltaLiquidity = pendingDelta > availableQuote ?
        availableQuote : pendingDelta;

    availableQuote -= liquidity.pendingDeltaLiquidity;
```
This will also bias the linked amounts calculations, liquidity's reservedCollatLiquidity, freeLiquidity and burnableLiquidity:
sol#L958-L975
```solidity
liquidity.pendingDeltaLiquidity = pendingDelta > availableQuote ?
    availableQuote : pendingDelta;

availableQuote -= liquidity.pendingDeltaLiquidity;
// Only reserve lockedCollateral x scalingFactor which unlocks more liquidity
// No longer need to lock one ETH worth of quote per call sold
uint reservedCollatLiquidity =
    lockedCollateral.quote.multiplyDecimal(lpParams.putCollatScalingFactor) +
    lockedCollateral.base.multiplyDecimal(basePrice).multiplyDecimal(lpParams.callCollatScalingFactor);

liquidity.reservedCollatLiquidity = availableQuote > reservedCollatLiquidity
    ? reservedCollatLiquidity
    : availableQuote;
availableQuote -= liquidity.reservedCollatLiquidity;
liquidity.freeLiquidity = availableQuote > reservedTokenValue ? availableQuote - reservedTokenValue : 0;

liquidity.burnableLiquidity = availableQuote;
liquidity.longScaleFactor = longScaleFactor;
return liquidity;
}
```
This affects all the functions relying on liquidity to control protocol risk. For example, the transferQuoteToHedge() limiting will be biased, sometimes limiting too strict, sometimes otherwise:
sol#L1037-L1055
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
Also, new position opening is controlled with trade.liquidity.freeLiquidity:
.sol#L882-L916
```solidity
/// @dev send/receive quote or base to/from LiquidityPool on position open
function _routeLPFundsOnOpen(TradeParameters memory trade, uint totalCost, uint feePortion) internal {
    if (trade.amount == 0) {
        return;
    }
    if (trade.optionType == OptionType.LONG_CALL) {
        liquidityPool.lockCallCollateral(trade.amount, trade.spotPrice,
            trade.liquidity.freeLiquidity);
        _transferFromQuote(msg.sender, address(liquidityPool), totalCost - feePortion);
        _transferFromQuote(msg.sender, address(this), feePortion);
    } else if (trade.optionType == OptionType.LONG_PUT) {
        liquidityPool.lockPutCollateral(trade.amount.multiplyDecimal(trade.strikePrice), trade.liquidity.freeLiquidity);
        _transferFromQuote(msg.sender, address(liquidityPool), totalCost - feePortion);
        _transferFromQuote(msg.sender, address(this), feePortion);
    } else if (trade.optionType == OptionType.SHORT_CALL_BASE) {
        liquidityPool.sendShortPremium(
            msg.sender,
            trade.amount,
            totalCost,
            trade.liquidity.freeLiquidity,
            feePortion,
            true
        );
    } else {
        // OptionType.SHORT_CALL_QUOTE || OptionType.SHORT_PUT_QUOTE
        liquidityPool.sendShortPremium(
            address(shortCollateral),
            trade.amount,
            totalCost,
            trade.liquidity.freeLiquidity,
            feePortion,
            false
        );
    }
}
```
For example, lockCallCollateral() and lockPutCollateral():
sol#L586-L590
```solidity
function lockCallCollateral(uint amount, uint spotPrice, uint freeLiquidity) external onlyOptionMarket {
    _checkCanHedge(amount, true);
    if (amount.multiplyDecimal(spotPrice).multiplyDecimal(lpParams.callCollatScalingFactor) > freeLiquidity) {
        revert LockingMoreQuoteThanIsFree(
```
sol#L570-L572
```solidity
function lockPutCollateral(uint amount, uint freeLiquidity) external onlyOptionMarket {
    if (amount.multiplyDecimal(lpParams.putCollatScalingFactor) > freeLiquidity) {
        revert LockingMoreQuoteThanIsFree(address(this), amount, freeLiquidity, lockedCollateral);
```
That is, if, for instance, there is a substantial enough unrealized negative P&L on the hedging position it will be recognized in NAV, but will not be properly accounted for in free liquidity value, so the positions will be allowed to be opened that will require hedging that may not be possible given real current liquidity, i.e. one after netting of the current P&L. Increasing the leverage might not be always sufficient in such situations. When effective leverage be placed high enough this will bring the hedging to the brink of liquidation that will remove the hedging altogether and expose the pool.

## Recommendation
Consider using marked to market values in getHedgingLiquidity().
