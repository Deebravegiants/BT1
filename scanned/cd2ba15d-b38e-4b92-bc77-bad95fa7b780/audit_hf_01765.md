# [H] If users withdraw while a position is in loss, the whole PNL of the position to their withdrawal amount instead of just their share of it.

## Summary
Severity: High
Contest weight: 0.7856
Dataset id: 9776
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _withdraw(uint256 depositId, bytes memory metadata, MarketPrices memory prices) internal {
    uint256 shares = depositInfo[depositId].shares;
    if (shares == 0) {
      revert Error.ZeroValue();
    }
    
    if (positionIsClosed) {
      _handleReturn(0, true, false);
    } else if (isLongOneLeverage(beenLong)) {  // beenLong && leverage == BASISPOINTS_DIVISOR
      uint256 swapAmount = IERC20(indexToken).balanceOf(address(this)) * shares / totalShares;
      nextAction.selector = NextActionSelector.SWAP_ACTION;
      // abi.encode(swapAmount, swapDirection): if swap direction is true, swap collateralToken to indexToken
      nextAction.data = abi.encode(swapAmount, false);
    } else if (curPositionKey == bytes32(0)) {    // vault liquidated
      _handleReturn(0, true, false);
    } else {
      IVaultReader.PositionData memory positionData = vaultReader.getPositionInfo(curPositionKey, prices);
      uint256 collateralDeltaAmount = positionData.collateralAmount * shares / totalShares;
      uint256 sizeDeltaInUsd = positionData.sizeInUsd * shares / totalShares;
      // we always charge the position fee of negative price impact case.
      uint256 feeAmount = vaultReader.getPositionFeeUsd(market, sizeDeltaInUsd, false) / prices.shortTokenPrice.max;
      int256 pnl = vaultReader.getPnl(curPositionKey, prices, sizeDeltaInUsd);
      if (pnl < 0) {
        collateralDeltaAmount = collateralDeltaAmount - feeAmount - uint256(-pnl) / prices.shortTokenPrice.max;
      } else {
        collateralDeltaAmount = collateralDeltaAmount - feeAmount;
      }
      uint256 acceptablePrice = abi.decode(metadata, (uint256));
      _createDecreasePosition(collateralDeltaAmount, sizeDeltaInUsd, beenLong, acceptablePrice, prices);
    }
  }
```
When a user withdraw while a short or long with more than 1x leverage is open, the vault first settles the fee via PerpetualVault.sol::settle() and calls _withdraw() in the next action executed by the keeper. When calculating how much to withdraw for the user depending on his shares, the vault applies the whole PNL of the position instead of the user's share of PNL due to wrong boolean input in VaultReader.sol::getPnl(). If the position is in loss, the PNL will return a negative value, which will be deducted from the user's withdrawing collateral amount. If a user's collateral is less than the PNL of the whole position, it will revert with an underflow error. If he has enough collateral, he will be taking on all the loss of the position instead of just his share of loss.

In _withdraw(), when a short or long with more than 1x leverage position is open, it calculates the user's collateral, size in usd value and fee amount to pay based on his shares.

```solidity
function getPnl(
  bytes32 key,
  MarketPrices memory prices,
  uint256 sizeDeltaUsd
) external view returns (int256) {
  uint256 sizeInTokens = getPositionSizeInUsd(key);
  if (sizeInTokens == 0) return 0;
  
  PositionInfo memory positionInfo = gmxReader.getPositionInfo(
    address(dataStore),
    referralStorage,
    key,
    prices,
    sizeDeltaUsd,
    address(0),
    true
  );

  return positionInfo.pnlAfterPriceImpactUsd;
}
```
In order to get the PNL of the user's share, the function calls VaultReader.getPnl(), which fetch the position info from GMX.

When calling getPositionInfo() on the gmxReader, is passed in true for the last input parameter. This is a mistake as it makes the function returns the whole position's PNL and not based on the position size in usd value of the user.

```solidity
function getPositionInfo(
    DataStore dataStore,
    IReferralStorage referralStorage,
    bytes32 positionKey,
    MarketUtils.MarketPrices memory prices,
    uint256 sizeDeltaUsd,
    address uiFeeReceiver,
    bool usePositionSizeAsSizeDeltaUsd
) public view returns (ReaderPositionUtils.PositionInfo memory) {
    return
        ReaderPositionUtils.getPositionInfo(
            dataStore,
            referralStorage,
            positionKey,
            prices,
            sizeDeltaUsd,
            uiFeeReceiver,
            usePositionSizeAsSizeDeltaUsd
        );
}
```
In GMX's ReaderPositionUtils.sol::getPositionInfo(), it calls the internal version of the function.

```solidity
function getPositionInfo(
    DataStore dataStore,
    IReferralStorage referralStorage,
    bytes32 positionKey,
    MarketUtils.MarketPrices memory prices,
    uint256 sizeDeltaUsd,
    address uiFeeReceiver,
    bool usePositionSizeAsSizeDeltaUsd
) public view returns (PositionInfo memory) {
    Position.Props memory position = PositionStoreUtils.get(dataStore, positionKey);
    return getPositionInfo(
        dataStore,
        referralStorage,
        position,
        prices,
        sizeDeltaUsd,
        uiFeeReceiver,
        usePositionSizeAsSizeDeltaUsd
    );
}
```
In the internal version, when this is true it sets the sizeDeltaInUsd variable (which was the user's share of usd value of the position) to the position's usd value.

```solidity
function getPositionInfo(
    DataStore dataStore,
    IReferralStorage referralStorage,
    Position.Props memory position,
    MarketUtils.MarketPrices memory prices,
    uint256 sizeDeltaUsd,
    address uiFeeReceiver,
    bool usePositionSizeAsSizeDeltaUsd
) internal view returns (PositionInfo memory) {
    if (position.account() == address(0)) {
        revert Errors.EmptyPosition();
    }

    PositionInfo memory positionInfo;
    GetPositionInfoCache memory cache;

    positionInfo.position = position;
    cache.market = MarketStoreUtils.get(dataStore, positionInfo.position.market());
    cache.collateralTokenPrice = MarketUtils.getCachedTokenPrice(positionInfo.position.collateralToken(), cache.market, prices);

    if (usePositionSizeAsSizeDeltaUsd) {
        sizeDeltaUsd = positionInfo.position.sizeInUsd();
    }
    ....
 (positionInfo.basePnlUsd, positionInfo.uncappedBasePnlUsd, / sizeDeltaInTokens /) = PositionUtils.getPositionPnlUsd(
        dataStore,
        cache.market,
        prices,
        positionInfo.position,
        sizeDeltaUsd
    );
```
which is later used to calculate the position's PNL via PositionUtils.sol::getPositionPnlUsd().

```solidity
function getPositionPnlUsd(
    DataStore dataStore,
    Market.Props memory market,
    MarketUtils.MarketPrices memory prices,
    Position.Props memory position,
    uint256 sizeDeltaUsd
) public view returns (int256, int256, uint256) {
    GetPositionPnlUsdCache memory cache;

    uint256 executionPrice = prices.indexTokenPrice.pickPriceForPnl(position.isLong(), false);

    // position.sizeInUsd is the cost of the tokens, positionValue is the current worth of the tokens
    cache.positionValue = (position.sizeInTokens() * executionPrice).toInt256();
    cache.totalPositionPnl = position.isLong() ? cache.positionValue - position.sizeInUsd().toInt256() : position.sizeInUsd().toInt256() - cache.positionValue;
    cache.uncappedTotalPositionPnl = cache.totalPositionPnl;

    if (cache.totalPositionPnl > 0) {
        cache.pnlToken = position.isLong() ? market.longToken : market.shortToken;
        cache.poolTokenAmount = MarketUtils.getPoolAmount(dataStore, market, cache.pnlToken);
        cache.poolTokenPrice = position.isLong() ? prices.longTokenPrice.min : prices.shortTokenPrice.min;
        cache.poolTokenUsd = cache.poolTokenAmount * cache.poolTokenPrice;
        cache.poolPnl = MarketUtils.getPnl(
            dataStore,
            market,
            prices.indexTokenPrice,
            position.isLong(),
            true
        );

        cache.cappedPoolPnl = MarketUtils.getCappedPnl(
            dataStore,
            market.marketToken,
            position.isLong(),
            cache.poolPnl,
            cache.poolTokenUsd,
            Keys.MAXPNLFACTORFORTRADERS
        );

        if (cache.cappedPoolPnl != cache.poolPnl && cache.cappedPoolPnl > 0 && cache.poolPnl > 0) {
            cache.totalPositionPnl = Precision.mulDiv(cache.totalPositionPnl.toUint256(), cache.cappedPoolPnl, cache.poolPnl.toUint256());
        }
    }

    if (position.sizeInUsd() == sizeDeltaUsd) {
        cache.sizeDeltaInTokens = position.sizeInTokens();
    } else {
        if (position.isLong()) {
            cache.sizeDeltaInTokens = Calc.roundUpDivision(position.sizeInTokens() * sizeDeltaUsd, position.sizeInUsd());
        } else {
            cache.sizeDeltaInTokens = position.sizeInTokens() * sizeDeltaUsd / position.sizeInUsd();
        }
    }

    cache.positionPnlUsd = Precision.mulDiv(cache.totalPositionPnl, cache.sizeDeltaInTokens, position.sizeInTokens()); 
    //sizeDeltaInTokens == sizeInTokens()
    cache.uncappedPositionPnlUsd = Precision.mulDiv(cache.uncappedTotalPositionPnl, cache.sizeDeltaInTokens, position.sizeInTokens());

    return (cache.positionPnlUsd, cache.uncappedPositionPnlUsd, cache.sizeDeltaInTokens);
}
```
Here the function calculates the totalPnl and calculate what percentage of the PNL to return based on sizeDeltaInUsd the caller inputted. However, since sizeDeltaInUsd was set to the position's sizeDeltaInUsd due to the usePositionSizeAsSizeDeltaUsd being true, this makes the function returns the totalPnl.

When the position is in loss and total PNL of the position is larger than the user's collateral amount (user has a few percentage of the vault + position is in loss), this negative PNL value which will be deducted from the collateral amount of the user in _withdraw() will cause an underflow revert.

Users may not be able to withdraw due to underflow revert or take on the loss of the whole position.

## Recommendation
Pass in false for usePositionSizeAsSizeDeltaUsd in gmxReader.getPositionInfo().
