# [H] 6.7 Violation of Maximum Ratio of Float Liquidity

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Specification Changed

The amount of liquidity supplied as float should be less than a threshold value, hard coded to 80% in the
current version of the contract. This restriction is enforced in the function addFloat() as follows:

```
function addFloat(Data storage reserve, uint256 delLiquidity) internal {
reserve.float += delLiquidity.toUint128();
if ((reserve.float * 1000) / reserve.liquidity > 800) revert LiquidityError();
}
```
This restriction is enforced only when a liquidity provider supplies its liquidity as float, but it does not hold
always as any liquidity provider can freely remove available liquidity from the pool. For example, if the
float liquidity is at its maximum level (i.e., 80%), one liquidity provider could call the
function remove() to remove the 20% of the remaining liquidity, thus putting the pool reserve in a
state with 100% of its liquidity as float.

```
function remove(
Data storage reserve,
uint256 delRisky,
uint256 delStable,
uint256 delLiquidity,
uint32 blockTimestamp
) internal {
reserve.reserveRisky -= delRisky.toUint128();
reserve.reserveStable -= delStable.toUint128();
reserve.liquidity -= delLiquidity.toUint128();
update(reserve, blockTimestamp);
}
```
```
Version 2 Code corrected
```
The Reserve library now defines a function checkUtilization() which checks if the invariant holds
whenever float is added, float is payed, or the liquidity is removed.

```
Version 3
Version 3
```
: Specification changed The respective code has been removed according to the new
specifications of.
