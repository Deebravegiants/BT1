# [M] 6.4 Total LP Shares Are Capped in Pools

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Specification Changed

The function _addLiquidity performs two checks to guarantee that an LP will get non-zero token
amounts from a small loan, both on repay and default. The checks are implemented as follows:

```
if (
((minLoan * BASE) / totalLpShares) * newLpShares == 0 ||
(((10**COLL_TOKEN_DECIMALS * minLoan) / maxLoanPerColl) * BASE) /
totalLpShares == 0
) revert PotentiallyZeroRoundedFutureClaims();
```
The first condition evaluates to true whenever totalLpShares > minLoan * BASE. Since both
minLoan and Base are fixed for a pool, the totalLpShares is capped for a pool.

Similarly, the second condition evaluates to true whenever totalLpShares > ((10**COLL_TOKEN_
DECIMALS * minLoan) / maxLoanPerColl) * BASE) sets another restriction on the maximum
totalLpShares.

Capping the totalLpShares prevents adding liquidity to pools that are attractive to users and have
high activity.

Specification changed

The specifications have changed and the checks described above have been removed, hence the
unintended capping on total LP shares is not present anymore.
