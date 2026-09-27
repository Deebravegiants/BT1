# [H] 6.6 Incorrect TVL Conversion

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 3 Code Corrected

The function _getTvlToken0 incorrectly converts the TVL amount of a given token i into token 0. The
oracle returns a price in x96 format. This price is directly used as if it would be a correctly formatted price
to convert the amounts. As the TVL in most cases will be lower than the price in x96 format the
calculation will return 0.

```
tvl0 = tvls[0];
for (uint256 i = 1; i < tvls.length; i++) {
(uint256[] memory prices, ) = oracle.price(tokens[0], tokens[i], 0x28);
require(prices.length > 0, ExceptionsLibrary.VALUE_ZERO);
uint256 price = 0;
for (uint256 j = 0; j < prices.length; j++) {
price += prices[j];
}
price /= prices.length;
tvl0 += tvls[i] / price;
```
Additionally, the calculation would be more precise if the price would be multiplied to convert the
amounts.

Code corrected:

The issue about the conversion of TVLs in function _getTvlToken0 has been addressed. The last
statement of the for-loop has been changed:

```
tvl0 += FullMath.mulDiv(tvls[i], CommonLibrary.Q96, priceX96);
```
