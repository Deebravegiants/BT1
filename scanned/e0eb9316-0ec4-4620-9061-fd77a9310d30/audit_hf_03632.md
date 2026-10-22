# [M] longScaleFactor for an expired board can be

## Summary
Severity: Medium
Contest weight: 0.6025
Dataset id: 19701
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
NAV can be increased as totalQueuedDeposits can be dropped down via
processDepositQueue() right before settleExpiredBoard() call.
Bob the board payoff beneficiary can atomically run processDepositQueue(), then
settleExpiredBoard() (both are public) right after big new deposit request to
enhance the resulting NAV that will be used for longScaleFactor calculation of his
board.
As a result of processDepositQueue() NAV will be increased by the full processed
deposit value, processedDeposits, but will be decreased only by DecimalMath.UNIT
- lpParams.adjustmentNetScalingFactor part of it.
Bob can back-run large initiateDeposit() calls with such a settlement. Bob's board
will take advantage from local increase of liquidity conditions as the expense of
other board settlements who do not time their settleExpiredBoard() calls.
Suppose deposits and withdrawals have some distribution reasonably close to
random. By picking the right moment Bob's board will gain artificially bigger
longScaleFactor and payouts that are linked to it, at the expense of other boards.
I.e. say there is one deposit and one withdrawal, Bob back-runs the deposit and
gained the corresponding payout boost. Other board will be settled in a less
favourable time, say around withdrawal, and will obtain lesser payout just by
the sake of this timing.
For the beneficiaries of the settlements of distinct boards it's a kind of zero sum
game and the winning scenario can be forced this way at the expense of other
parties.
The impact is other boards lose money as Bob has indirectly stolen from them. In
absence of any significant prerequisites setting the severity to be high.
processDepositQueue() increases NAV by processedDeposits and decreases it by
(DecimalMath.UNIT - lpParams.adjustmentNetScalingFactor) * processedDeposits
by adding it to protectedQuote:
sol#L392-L399
```solidity
// only update if deposit processed to avoid changes when CB's are firing
if (processedDeposits != 0) {
    totalQueuedDeposits -= processedDeposits;
    protectedQuote = (liquidity.NAV + processedDeposits).multiplyDecimal(
        DecimalMath.UNIT - lpParams.adjustmentNetScalingFactor
    );
}
```
NAV is determined off live LiquidityPool and GMX (usedDeltaLiquidity) NPV of the
assets less protectedQuote:
sol#L898-L921
```solidity
function _getTotalPoolValueQuote(
    uint basePrice,
    uint usedDeltaLiquidity,
    int optionValueDebt
) internal view returns (uint, uint) {
    int totalAssetValue = SafeCast.toInt256(
        ConvertDecimals.convertTo18(quoteAsset.balanceOf(address(this)), quoteAsset.decimals()) +
        ConvertDecimals.convertTo18(baseAsset.balanceOf(address(this)), baseAsset.decimals()).multiplyDecimal(basePrice)
    ) +
    SafeCast.toInt256(usedDeltaLiquidity) -
    SafeCast.toInt256(totalOutstandingSettlements + totalQueuedDeposits);
    if (totalAssetValue < 0) {
        revert NegativeTotalAssetValue(address(this), totalAssetValue);
    }
    // If debt is negative we can simply return TAV - (-debt)
    // availableAssetValue here is +'ve and optionValueDebt is -'ve so we can safely return uint
    if (optionValueDebt < 0) {
        return (SafeCast.toUint256(totalAssetValue - optionValueDebt), DecimalMath.UNIT);
    }
    // ensure a percentage of the pool's NAV is always protected from AMM's insolvency
    int availableAssetValue = totalAssetValue - int(protectedQuote);
```
longScaleFactor is determined via liquidity as of closing time:
sol#L670-L699
```solidity
function boardSettlement(
    uint insolventSettlements,
    uint amountQuoteFreed,
    uint amountQuoteReserved,
    uint amountBaseFreed
) external onlyOptionMarket returns (uint) {
    // Update circuit breaker whenever a board is settled, to pause deposits/withdrawals
    // This allows keepers some time to settle insolvent positions
    if (block.timestamp + cbParams.boardSettlementCBTimeout > CBTimestamp) {
        CBTimestamp = block.timestamp + cbParams.boardSettlementCBTimeout;
        emit BoardSettlementCircuitBreakerUpdated(CBTimestamp);
    }
    insolventSettlementAmount += insolventSettlements;
    _freePutCollateral(amountQuoteFreed);
    _freeCallCollateral(amountBaseFreed);
    // If amountQuoteReserved > available liquidity, amountQuoteReserved is scaled down to an available amount
    Liquidity memory liquidity = getLiquidity(); // calculates total pool value and potential scaling
    totalOutstandingSettlements += amountQuoteReserved.multiplyDecimal(liquidity.longScaleFactor);
    emit BoardSettlement(insolventSettlementAmount, amountQuoteReserved, totalOutstandingSettlements);
    if (address(poolHedger) != address(0)) {
        poolHedger.resetInteractionDelay();
    }
    return liquidity.longScaleFactor;
}
```
It is then recorded to scaledLongsForBoard in _settleExpiredBoard():
.sol#L1051-L1104
```solidity
function _settleExpiredBoard(OptionBoard memory board) internal {
    uint spotPrice = exchangeAdapter.getSettlementPriceForMarket(address(this), board.expiry);
    ...
    (uint lpBaseInsolvency, uint lpQuoteInsolvency) = shortCollateral.boardSettlement(
        totalAMMShortCallProfitBase,
        totalAMMShortPutProfitQuote + totalAMMShortCallProfitQuote
    );
    // This will batch all base we want to convert to quote and sell it in one transaction
    uint longScaleFactor = liquidityPool.boardSettlement(
        lpQuoteInsolvency + lpBaseInsolvency.multiplyDecimal(spotPrice),
        totalBoardLongPutCollateral,
        totalUserLongProfitQuote,
        totalBoardLongCallCollateral
    );
    scaledLongsForBoard[board.id] = longScaleFactor;
```
Then used in settlements:
al.sol#L179-L214
```solidity
function settleOptions(uint[] memory positionIds) external nonReentrant notGlobalPaused {
    // This is how much is missing from the ShortCollateral contract that was claimed by LPs at board expiry
    // We want to take it back when we know how much was missing.
    uint baseInsolventAmount = 0;
    uint quoteInsolventAmount = 0;
    OptionToken.PositionWithOwner[] memory optionPositions = optionToken.getPositionsWithOwner(positionIds);
    optionToken.settlePositions(positionIds);
    uint positionsLength = optionPositions.length;
    for (uint i = 0; i < positionsLength; ++i) {
        OptionToken.PositionWithOwner memory position = optionPositions[i];
        uint settlementAmount = 0;
        uint insolventAmount = 0;
        (uint strikePrice, uint priceAtExpiry, uint ammShortCallBaseProfitRatio, uint longScaleFactor) = optionMarket.getSettlementParameters(position.strikeId);
        if (priceAtExpiry == 0) {
            revert BoardMustBeSettled(address(this), position);
        }
        if (position.optionType == OptionMarket.OptionType.LONG_CALL) {
            settlementAmount = _sendLongCallProceeds(
                position.owner,
                position.amount.multiplyDecimal(longScaleFactor),
                strikePrice,
                priceAtExpiry
            );
        } else if (position.optionType == OptionMarket.OptionType.LONG_PUT) {
            settlementAmount = _sendLongPutProceeds(
                position.owner,
                position.amount.multiplyDecimal(longScaleFactor),
                strikePrice,
                priceAtExpiry
            );
        }
```
This way Bob have direct payoff boost from the longScaleFactor increase.

## Recommendation
Notice that withdrawal processing have similar, but opposite effect (although a bit
more complicated due to token price also depending on NAV): some amount is
removed from the balance, but only part of it is cleared from protectedQuote, so
NAV decreases. For example, it can be used for griefing in a similar setting.
One of the possible approaches might be restricting both processDepositQueue()
and processWithdrawalQueue() to be run by a protocol controlled keeper script
only. There a condition for it to be run might be both time and deposit-withdrawal
balance dependent, i.e., as an example, it can run not less frequently that once per
24h, but tend to run in situations when total amounts of deposits and withdrawals
are reasonably close to minimize the NAV impact.
