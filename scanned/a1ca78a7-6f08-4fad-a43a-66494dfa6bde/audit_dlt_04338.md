# [M] FixedInterestRateModel.sol#L69 : getSupplyRate can be updated to consider the one more factor utilizationRate like how compound works.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/161
Type: sherlock-finding

## Details
ak1

medium

# FixedInterestRateModel.sol#L69 : getSupplyRate can be updated to consider the one more factor utilizationRate like how compound works.

## Summary
FixedInterestRateModel.sol#L69 : getSupplyRate can be updated to consider the one more factor `utilizationRate` like how compound works.

## Vulnerability Detail
The  `getSupplyRate` is done in following way. This always give constant value for a given asset. It does not consider the fluctuation in the market. Such as how is much is utilised.

https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/market/FixedInterestRateModel.sol#L69-L73

Whereas, the compound protocol considers the `utilizationRate`, please refer the below line of codes.

https://github.com/compound-finance/compound-protocol/blob/a3214f67b73310d547e00fc578e8355911c9d376/contracts/WhitePaperInterestRateModel.sol#L79-L83

    function getSupplyRate(uint cash, uint borrows, uint reserves, uint reserveFactorMantissa) override public view returns (uint) {
        uint oneMinusReserveFactor = BASE - reserveFactorMantissa;
        uint borrowRate = getBorrowRate(cash, borrows, reserves);
        uint rateToPool = borrowRate * oneMinusReserveFactor / BASE;
        return utilizationRate(cash, borrows, reserves) * rateToPool / BASE;

above method is handling the case when borrow is zero. whereas the union is not considering if the borrow is zero.

## Impact
The current method always use the constant set of supply rate irrespective of the market fluctuations.
The Borrows being 0 case might also not be fully accounted for.

The protocol may not be healthy enough to deal all the market conditions.

## Code Snippet

https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/market/FixedInterestRateModel.sol#L69-L73

The `getSupplyRate` is called in following places,
https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/market/UToken.sol#L445-L447

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/161_
