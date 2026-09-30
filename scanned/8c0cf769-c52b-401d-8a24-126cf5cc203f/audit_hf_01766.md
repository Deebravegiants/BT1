# [H] Subtracting position fee in position net value will lead to incorrect share allocation

## Summary
Severity: High
Contest weight: 0.7853
Dataset id: 9777
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In order to calculate how much shares should be minted per user deposit, we need to get the net value of the position and calculate shares proportional of the user deposit (actual increase of position). Removing the position fee in the calculation of net value is not correct and will lead to unfair shares distribution.

Shares for user deposit are calculated in PerpetualVault::_mint():
_shares = amount * totalShares / totalAmountBefore;

where totalAmountBefore is calculated as:
totalAmountBefore = _totalAmount(prices) - amount;

```solidity
function _totalAmount(MarketPrices memory prices) internal view returns (uint256) {
  if (positionIsClosed) {
    return collateralToken.balanceOf(address(this));
  } else {
    IVaultReader.PositionData memory positionData = vaultReader.getPositionInfo(curPositionKey, prices);
    uint256 total = IERC20(indexToken).balanceOf(address(this)) * prices.indexTokenPrice.min / prices.shortTokenPrice.min
    + collateralToken.balanceOf(address(this))
    + positionData.netValue / prices.shortTokenPrice.min;

    return total;
  }
}
```
In VaultReader::getPositionInfo() we have the following to get the netValue:

```solidity
uint256 netValue = 
  positionInfo.position.numbers.collateralAmount * prices.shortTokenPrice.min +
  positionInfo.fees.funding.claimableLongTokenAmount * prices.longTokenPrice.min +
  positionInfo.fees.funding.claimableShortTokenAmount * prices.shortTokenPrice.min -
  positionInfo.fees.borrowing.borrowingFeeUsd -
  positionInfo.fees.funding.fundingFeeAmount * prices.shortTokenPrice.min -
  positionInfo.fees.positionFeeAmount * prices.shortTokenPrice.min;
  
if (positionInfo.basePnlUsd >= 0) {
  netValue = netValue + uint256(positionInfo.basePnlUsd);
} else {
  netValue = netValue - uint256(-positionInfo.basePnlUsd);
}
```
We have already adjusted user's actual increase of position in afterOrderExecution():

```solidity
if (flow == FLOW.DEPOSIT) {
    uint256 amount = depositInfo[counter].amount;
    uint256 feeAmount = vaultReader.getPositionFeeUsd(market, orderResultData.sizeDeltaUsd, false) / prices.shortTokenPrice.min;
    uint256 prevSizeInTokens = flowData;
    int256 priceImpact = vaultReader.getPriceImpactInCollateral(curPositionKey, orderResultData.sizeDeltaUsd, prevSizeInTokens, prices);
    uint256 increased;
    if (priceImpact > 0) {
      increased = amount - feeAmount - uint256(priceImpact) - 1;
    } else {
      increased = amount - feeAmount + uint256(-priceImpact) - 1;
    }
    _mint(counter, increased, false, prices);
    nextAction.selector = NextActionSelector.FINALIZE;
  } else {
    _updateState(false, orderResultData.isLong);
  }
```
Removing the position fee from the netValue of a position would result in better shares allocation for late depositors. Position fee should not be accounted in the net value as it is taken from increase/decrease amounts in GMX and fee is static percent of the position size.

Consider the following example (for the purpose of example, we can consider that there is not a borrowing/funding fee and price of index token between to increase operations is the same):

We have a position with $1000 collateral and $3000 position size in USD. Lets say position fee is 0.33% (it is calculated based on position size) and we have 1000e14 total shares (1000e6 / 1e8)
Alice deposits $1000 worth of collateral and gets 1000e6 * totalShares / (1000e6 - (positionFee)) shares which is equal to 1000e6 * 1000e14 / (1000e6 - 10e6) which makes 99999999990000000 shares
Bob deposits $1000 shares right after Alice and since price of index token is the same and there are no funding/borrowing fees, Bob is expected to get the same amount of shares.
Calculating Bob's shares we got 1000e6 * (1000e14 + Alice's shares) / (1000e6 + Alice's increase - positionFee) which is equal to 1000e6 * (1000e14 + 99999999990000000) / uint(1990e6 - 20e6) which makes 101522842634517766
Every consecutive depositor will be getting more and more shares than what is fair.

Incorrect shares allocation.

## Recommendation
Do not use positionFee when calculating netValue of a position.
