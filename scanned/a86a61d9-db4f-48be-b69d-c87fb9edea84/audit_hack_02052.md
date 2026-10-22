# [H] 6.3 Borrower Locks Liquidity in the Pool

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Specification Changed

Calling the function borrow() with a given delLiquidity triggers the call
reserve.borrowFloat() which decreases the amount of available float in the pool and increases the
debt of the pool reserve accordingly. This way, the borrower locks delLiquidity from the available
float in the pool reserve. Below is the borrowFloat function.

```
function borrowFloat(Data storage reserve, uint256 delLiquidity) internal {
reserve.float -= delLiquidity.toUint128();
reserve.debt += delLiquidity.toUint128();
}
```
A liquidity provider that has supplied its liquidity as float needs to first call the function claim() which
converts the float into liquidity before removing the liquidity from the pool. However, the only way for all
liquidity providers to claim all their float liquidities is if all borrowers call the function repay() which
triggers a call to reserve.repayFloat():

```
function repayFloat(Data storage reserve, uint256 delLiquidity) internal {
reserve.float += delLiquidity.toUint128();
reserve.debt -= delLiquidity.toUint128();
}
```
But, if the price of the risky token is below the strike price, the borrower has no incentive to call the
function repay(), therefore potentially keeping locked the float liquidity. Moreover, the function
repay() does not impose any time restriction to borrowers when they can exercise their option, i.e., the
borrower can potentially call the repay() function at an arbitrary time after the maturity. This puts
pressure on the liquidity providers to call it themselves which is possible because in the current version of
the PrimitiveEngine contract, anyone can call the function repay() after the maturity of the
pool. If liquidity provider have the burden to call the functions, they also bear the costs.

```
Version 2 Specification changed
```
This version of the code introduces a grace period, around 24h, to permit only borrowers calling the
function repay() after pool's maturity. In case a borrower does not call the function during this period,
anyone can call the function repay() and exit the borrowers' positions, therefore releasing the locked
liquidity. Still, the additional costs need to be payed by the caller / LP if they call it to relase their funds.

```
Version 3 Specification changed
```
The respective code has been removed according to the new specifications of Version 3.
