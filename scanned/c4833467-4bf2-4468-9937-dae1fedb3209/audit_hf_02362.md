# [H] Improper Total Funding Fee Calculation in Position

## Summary
Severity: High
Contest weight: 0.7807
Dataset id: 12792
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, PRINT3R is a perpetual futures protocol that is designed to create permissionless trading markets. And the user positions are managed in a core Position contract. While analyzing the position-related funding fee collection, we notice the fee amount is incorrectly calculated. In the following, we show the implementation of the related routine, i.e., `getTotalFundingFees()`. For a position, its funding fee is computed by multiplying the funding fee delta with the position size. It comes to our attention that the position size is maintained as a dollar amount. However, the multiplication makes use of the `percentageInt()` helper routine, which should be replaced with `percentageUsd()`.
```solidity
function getTotalFundingFees(MarketId _id, IMarket market, Data memory _position, uint256 _indexPrice) internal view returns (int256) {
    (, int256 nextFundingAccrued) = Funding.calculateNextFunding(_id, market, _position.ticker, _indexPrice);
    return _position.size.toInt256().percentageInt(nextFundingAccrued - _position.fundingParams.lastFundingAccrued);
}
```
Moreover, the related Borrow contract shares another related issue in its `calculatePendingFees()`. Specifically, the resulting `pendingFees` should be further adjusted with the elapsed time duration as follows: `borrowRate.percentage(timeElapsed, SECONDS_PER_DAY)` (line 126).
```solidity
function calculatePendingFees(MarketId _id, IMarket market, string calldata _ticker, bool _isLong) public view returns(uint256 pendingFees) {
    uint256 borrowRate = market.getBorrowingRate(_id, _ticker, _isLong);
    if (borrowRate == 0) return 0;
    uint256 timeElapsed = block.timestamp - market.getLastUpdate(_id, _ticker);
    if (timeElapsed == 0) return 0;
    pendingFees = borrowRate * timeElapsed;
}
```

## Recommendation
Revisit the above routine to properly compute a position's funding fee. Also, other related routines `_calculateFees()`, `_calculateAmountAfterFees()`, and `decreasePosition()` in Execution should also be improved for proper fee collection.
