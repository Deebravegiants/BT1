# [M] GoodDollarExchangeProvider::

## Summary
Severity: Medium
Contest weight: 0.6136
Dataset id: 1758
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GoodDollarExchangeProvider::mintFromExpansion() mints supply tokens while keeping
the current price constant. To achieve this, a certain formula is used, but in the process it
scales the reserveRatioScalar*exchange.reserveRatio to 1e8 precision (the precision of exchange.reserveRatio) down from 1e18.
However, the calculation of the new amount of tokens to mint is based on the full ratio
with 1e18, which will mint more tokens than it should and change the price, breaking the
readme.
est() due to using mul and then div, as mul divides by 1e18 unnecessarily in this case.
it calculates the ratio using the formula and then scales it down, changing the price.
In GoodDollarExchangeProvider:147, newRatio is calculated with full 1e18 precision and
used to calculate the amount of tokens to mint, but exchanges[exchangeId].reserveRatio
is stored with the downscaled value, newRatio/1e10, causing an error and price change.
This happens because the price is reserve/(supply*reserveRatio). As supply is increased
by a calculation that uses the full precision newRatio, but reserveRatio is stored with less
precision (1e8), the price will change due to this call.
Internal pre-conditions
None.
External pre-conditions
None.
Attack Path
1. GoodDollarExchangeProvider::mintFromExpansion() is called and a rounding error
happens in the calculation of newRatio.
The current price is modified due to the expansion which goes against the readme:
What properties/invariants do you want to hold even if breaking them has a
low/unknown impact?
Bancor formula invariant. Price = Reserve / Supply * reserveRatio

## Proof of Concept
Add the following test to GoodDollarExchangeProvider.t.sol:
```solidity
function test_POC_mintFromExpansion_priceChangeFix() public {
    uint256 priceBefore = exchangeProvider.currentPrice(exchangeId);
    vm.prank(expansionControllerAddress);
    exchangeProvider.mintFromExpansion(exchangeId, reserveRatioScalar);
    uint256 priceAfter = exchangeProvider.currentPrice(exchangeId);
    assertEq(priceBefore, priceAfter, "Price should remain exactly equal");
}
```
eliminating the rounding error, the price matches exactly (exact fix show below).

## Recommendation
Divide and multiply newRatio by 1e10 to eliminate the rounding error, keeping the price
unchanged.
```solidity
function mintFromExpansion(
    bytes32 exchangeId,
    uint256 reserveRatioScalar
) external onlyExpansionController whenNotPaused returns (uint256 amountToMint) {
    require(reserveRatioScalar > 0, "Reserve ratio scalar must be greater than 0");
    PoolExchange memory exchange = getPoolExchange(exchangeId);
    UD60x18 scaledRatio = wrap(uint256(exchange.reserveRatio) * 1e10);
    UD60x18 newRatio = wrap(unwrap(scaledRatio.mul(wrap(reserveRatioScalar))) / 1e10 * 1e10);
    ...
}
```
