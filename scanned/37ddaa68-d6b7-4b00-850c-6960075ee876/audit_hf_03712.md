# [H] Incorrect function call leads to stale borrow

## Summary
Severity: High
Contest weight: 0.7812
Dataset id: 19823
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to an incorrect function call while getting the total borrow fees, the returned fees will be an inaccurate and stale amount. Which will have an impact on liquidity providers.

As said the function getTotalBorrowingFees:
```solidity
function getTotalBorrowingFees(DataStore dataStore, address market, address longToken, address shortToken, bool isLong) internal view returns (uint256) {
    uint256 openInterest = getOpenInterest(dataStore, market, longToken, shortToken, isLong);
    uint256 cumulativeBorrowingFactor = getCumulativeBorrowingFactor(dataStore, market, isLong);
    uint256 totalBorrowing = getTotalBorrowing(dataStore, market, isLong);
    return openInterest * cumulativeBorrowingFactor - totalBorrowing;
}
```

calculates the fees by calling getCumulativeBorrowingFactor(...): cts/market/MarketUtils.sol#L1890 which is the wrong function to call because it returns a stale borrowing factor. To get the actual borrowing factor and calculate correctly the borrowing fees, GMX should call the getNextCumulativeBorrowingFactor function: cts/market/MarketUtils.sol#L1826 Which makes the right calculation, taking into account the stale fees also:
```solidity
uint256 durationInSeconds = getSecondsSinceCumulativeBorrowingFactorUpdated(dataStore, market.marketToken, isLong);
uint256 borrowingFactorPerSecond = getBorrowingFactorPerSecond(dataStore, market, prices, isLong);
uint256 cumulativeBorrowingFactor = getCumulativeBorrowingFactor(dataStore, market.marketToken, isLong);
uint256 delta = durationInSeconds * borrowingFactorPerSecond;
uint256 nextCumulativeBorrowingFactor = cumulativeBorrowingFactor + delta;
return (nextCumulativeBorrowingFactor, delta);
```

As fee calculation will not be accurate, liquidity providers will have a less-worth token because pending fees are not accounted in the pool's value.

## Recommendation
In order to mitigate the issue, call the function getNextCumulativeBorrowingFactor instead of the function getCumulativeBorrowingFactor() for a correct accounting and not getting stale fees.
