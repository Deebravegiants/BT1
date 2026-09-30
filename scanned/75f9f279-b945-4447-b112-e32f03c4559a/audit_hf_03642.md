# [M] New SHORT_CALL_QUOTE positions hedging

## Summary
Severity: Medium
Contest weight: 0.5934
Dataset id: 19711
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
New SHORT_CALL_QUOTE positions canHedge() check is performed as if pool delta is decreased as a result of a user selling call to it. As it is in fact increased, being a function of option type and not collateral type. The check is inverted and can lead to blocking good trades, i.e. function unavailability, and not blocking of the bad ones as the check can be omitted in the result with if !deltaIncreasing && expectedHedge >= 0 then allow logic of GMXFuturesPoolHedger's canHedge(), i.e. allowing to open a position that cannot be hedged. openPosition() with SHORT_CALL_QUOTE type invokes canHedge() check via sendShortPremium() with deltaIncreasing == false, while when call option is being sold to the pool delta increases no matter what collateral is being used, i.e. both for SHORT_CALL_BASE and SHORT_CALL_QUOTE, as the pool obtains a call with positive delta in both cases. Core part of the impact is that SHORT_CALL_QUOTE trades aren't checked to be hedgeable. Allowing a trade big enough so it cannot be hedged will force the protocol to be partially unhedged, i.e. sell some naked options. This can lead to delta initiated protocol wide losses quick enough. As trade opening can't be protocol controlled in any way, being always initiated by a user, no low probability prerequisites looks to be needed in this case, so, given the possibility of substantial enough losses, setting the severity to be high. canHedge() treats deltaIncreasing as whether it increases delta of the pool:
oolHedger.sol#L334-L359
```solidity
/**
* @dev return whether a hedge should be performed
*/
function canHedge(uint /* amountOptions */, bool deltaIncreasing) external view override returns (bool) {
    ...
    if (Math.abs(expectedHedge) <= Math.abs(currentHedge)) {
        // Delta is shrinking (potentially flipping, but still smaller than current hedge), so we skip the check
        return true;
    }
    if (deltaIncreasing && expectedHedge <= 0) {
        // expected hedge is negative, and trade increases delta of the pool
        return true;
    }
    if (!deltaIncreasing && expectedHedge >= 0) {
        return true;
    }
```
It's invoked via _checkCanHedge():
sol#L1028-L1035
```solidity
function _checkCanHedge(uint amountOptions, bool increasesDelta) internal view {
    if (address(poolHedger) == address(0)) {
        return;
    }
    if (!poolHedger.canHedge(amountOptions, increasesDelta)) {
        revert UnableToHedgeDelta(address(this), amountOptions, increasesDelta);
    }
}
```
sendShortPremium() uses _checkCanHedge() with deltaIncreasing = increasesDelta = isCall:
sol#L635-L660
```solidity
/**
* @notice Sends premium user selling an option to the pool.
* @dev The caller must be the OptionMarket.
*
* @param recipient The address of the recipient.
* @param amountContracts The number of contracts sold to AMM.
* @param premium The amount to transfer to the user.
* @param freeLiquidity The amount of free collateral liquidity.
* @param reservedFee The amount collected by the OptionMarket.
*/
function sendShortPremium(
    address recipient,
    uint amountContracts,
    uint premium,
    uint freeLiquidity,
    uint reservedFee,
    bool isCall
) external onlyOptionMarket {
    if (premium + reservedFee > freeLiquidity) {
        freeLiquidity);
    }
    // only blocks opening new positions if cannot hedge
    _checkCanHedge(amountContracts, isCall);
    _sendPremium(recipient, premium, reservedFee);
}
```
_routeLPFundsOnOpen() calls liquidityPool.sendShortPremium() with isCall == false for SHORT_CALL_QUOTE type:
.sol#L896-L915
```solidity
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
```
_openPosition() calls _routeLPFundsOnOpen():
.sol#L560-L595
```solidity
/**
* @dev Opens a position, which may be long call, long put, short call or short put.
*/
function _openPosition(TradeInputParameters memory params) internal returns (Result memory result) {
    (TradeParameters memory trade, Strike storage strike, OptionBoard storage board) = _composeTrade(
        ...
    );
    OptionMarketPricer.TradeResult[] memory tradeResults;
    (trade.amount, result.totalCost, result.totalFee, tradeResults) = _doTrade(
        ...
    );
    int pendingCollateral;
    // collateral logic happens within optionToken
    (result.positionId, pendingCollateral) = optionToken.adjustPosition(
        ...
    );
    uint reservedFee =
        result.totalFee.multiplyDecimal(optionMarketParams.feePortionReserved);
    _routeLPFundsOnOpen(trade, result.totalCost, reservedFee);
}
```
_openPosition() is called by user-facing openPosition():
.sol#L505-L514
```solidity
/**
* @notice Attempts to open positions within cost bounds.
* @dev If a positionId is specified that position is adjusted accordingly
*
* @param params The parameters for the requested trade
*/
function openPosition(TradeInputParameters memory params) external nonReentrant returns (Result memory result) {
    result = _openPosition(params);
    _checkCostInBounds(result.totalCost, params.minTotalCost, params.maxTotalCost);
}
```
This way for SHORT_CALL_QUOTE type sendShortPremium() involves canHedge() check with deltaIncreasing == false, i.e. as if increases delta of the pool is false:
.sol#L906-L914
```solidity
// OptionType.SHORT_CALL_QUOTE || OptionType.SHORT_PUT_QUOTE
liquidityPool.sendShortPremium(
    address(shortCollateral),
    trade.amount,
    totalCost,
    trade.liquidity.freeLiquidity,
    feePortion,
    false
);
```
In the same time SHORT_CALL_QUOTE is selling call to the pool for a premium, an operation that increases delta of the pool. I.e. no matter what collateral is used, the pool has additional call option being sold to it and this way has its delta increased. I.e. the hedging check in this case is reverted and can block good trades or allow the ones that can't be hedged. That is, remaining < absHedgeDiff.multiplyDecimal(futuresPoolHedgerParams.marketDepthBuffer) can hold, meaning that there is a shortage, but the canHedge() was already returned true via !deltaIncreasing && expectedHedge >= 0 condition, having deltaIncreasing == false for this type of call:
oolHedger.sol#L337-L373
```solidity
function canHedge(uint /* amountOptions */, bool deltaIncreasing) external view override returns (bool) {
    ...
    if (deltaIncreasing && expectedHedge <= 0) {
        // expected hedge is negative, and trade increases delta of the pool
        return true;
    }
    if (!deltaIncreasing && expectedHedge >= 0) {
        return true;
    }
    // remaining is the number of us dollars that can be hedged
    uint remaining = ConvertDecimals.convertTo18(
        (vault.poolAmounts(address(baseAsset)) -
        vault.reservedAmounts(address(baseAsset))),
        baseAsset.decimals()
    );
    uint absHedgeDiff = (Math.abs(expectedHedge) - Math.abs(currentHedge));
    if (remaining < absHedgeDiff.multiplyDecimal(futuresPoolHedgerParams.marketDepthBuffer)) {
        return false;
    }
    ...
}
```

## Recommendation
Consider checking hedging possibility for SHORT_CALL_QUOTE trades with _checkCanHedge(amountContracts, true).
