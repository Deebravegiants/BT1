# [M] \[M02\] Lack of SafeMath

## Summary
Severity: Medium
Source: https://github.com/mcdexio/mai-fund-protocol/blob/98af0d1d7e9872ba2b5e734e2a43c161ef635608/contracts/lib/LibEnumerableMap.sol
Type: audit-issue

## Details
In the [LibEnumerableMap library](https://github.com/mcdexio/mai-fund-protocol/blob/98af0d1d7e9872ba2b5e734e2a43c161ef635608/contracts/lib/LibEnumerableMap.sol), there are many instances where unprotected math operators are used. For example:

* [line 40](https://github.com/mcdexio/mai-fund-protocol/blob/98af0d1d7e9872ba2b5e734e2a43c161ef635608/contracts/lib/LibEnumerableMap.sol#L40) uses `-` operator
* [line 82](https://github.com/mcdexio/mai-fund-protocol/blob/98af0d1d7e9872ba2b5e734e2a43c161ef635608/contracts/lib/LibEnumerableMap.sol#L82) uses `-` operator
* [line 91](https://github.com/mcdexio/mai-fund-protocol/blob/98af0d1d7e9872ba2b5e734e2a43c161ef635608/contracts/lib/LibEnumerableMap.sol#L91) uses `-` operator
* [line 92](https://github.com/mcdexio/mai-fund-protocol/blob/98af0d1d7e9872ba2b5e734e2a43c161ef635608/contracts/lib/LibEnumerableMap.sol#L92) uses `+` and `/` operators
* [line 111](https://github.com/mcdexio/mai-fund-protocol/blob/98af0d1d7e9872ba2b5e734e2a43c161ef635608/contracts/lib/LibEnumerableMap.sol#L111) uses `-` operator

Consider using [SafeMath‘s](https://github.com/OpenZeppelin/openzeppelin-contracts-ethereum-package/blob/release-3.1/contracts/math/SafeMath.sol) corresponding functions instead of unprotected mathematical operators.

**Update:** _Fixed in [PR #5](https://github.com/mcdexio/mai-fund-protocol/pull/5)._
