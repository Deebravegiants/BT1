# [M] Reserves should not be considered part of the

## Summary
Severity: Medium
Contest weight: 0.7144
Dataset id: 17609
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The implementation is different from the documentation regarding the interest rate formula.
The formula given in the docs:
Calculates Borrow rate per second:
BorrowRatePerSecond = c3 × (util × c1 + util32 × c1 + util64 × c2) / secsPerYear
where, util = borrows / (liquidity - reserves + borrows)
util = borrows / (liquidityreserves + borrows)
https://github.com/sentimentxyz/protocol/blob/4e45871e4540df0f189f6c89deb8d34f24930120/src/tokens/LToken.sol#L217-L227
```solidity
function getRateFactor() internal view returns (uint) {
    return (block.timestamp == lastUpdated) ?
        0 :
        ((block.timestamp - lastUpdated)*1e18)
            .mulWadUp(
                rateModel.getBorrowRatePerSecond(
                    asset.balanceOf(address(this)),
                    borrows
                )
            );
}
```
However, the current implementation is taking all the balance as the liquidity:
https://github.com/sentimentxyz/protocol/blob/4e45871e4540df0f189f6c89deb8d34f24930120/src/core/DefaultRateModel.sol#L51-L68
```solidity
function getBorrowRatePerSecond(
    uint liquidity,
    uint borrows
)
    external
    view
    returns (uint)
{
    uint util = _utilization(liquidity, borrows);
    return c3.mulDivDown(
        (
            util.mulWadDown(c1)
            + util.rpow(32, SCALE).mulWadDown(c1)
            + util.rpow(64, SCALE).mulWadDown(c2)
        ),
        secsPerYear
    );
}
```
https://github.com/sentimentxyz/protocol/blob/4e45871e4540df0f189f6c89deb8d34f24930120/src/core/DefaultRateModel.sol#L70-L77
```solidity
function _utilization(uint liquidity, uint borrows)
    internal
    pure
    returns (uint)
{
    uint totalAssets = liquidity + borrows;
    return (totalAssets == 0) ? 0 : borrows.divWadDown(totalAssets);
}
```
Per the docs, when calculating the interest rate, util is the ratio of available liquidity to the borrows, available liquidity should not include reserves.
The current implementation is using all the balance as the liquidity, this will make the interest rate lower than expectation.

## Proof of Concept
Given:
• asset.address(this)+borrows=10000
• reserves=1500,borrows=7000
Expected result:
When calculating getRateFactor(), available liquidity should be asset.balanceOf(address(this))-reserves=1500,util=7000/8500=0.82, getBorrowRatePerSecond()=9114134329
Actual result:
When calculating getRateFactor(), asset.balanceOf(address(this))=3000,util=0.7e18, getBorrowRatePerSecond()=7763863430
The actual interest rate is only 7763863430/9114134329=85% of the expected rate.

## Recommendation
The implementation of getRateFactor() can be updated to:
```solidity
function getRateFactor() internal view returns (uint) {
    return (block.timestamp == lastUpdated) ?
        0 :
        ((block.timestamp - lastUpdated)*1e18)
            .mulWadUp(
                rateModel.getBorrowRatePerSecond(
                    asset.balanceOf(address(this)) - reserves,
                    borrows
                )
            );
}
```
Removed reserves from LToken and added an alternate mechanism to collect direct fees.
originationFee may result in the borrower account becoming liquidatable immediately (aka WP-M2).
riskEngine.isBorrowAllowed should be removed as it's no longer needed.
Pushed a commit to remove the redundant call to riskEngine. PR here.
