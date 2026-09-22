# [M] \[M06\] Unsafe casting

## Summary
Severity: Medium
Source: https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/TaxCollector.sol#L554
Type: audit-issue

## Details
In [line 554 of the TaxCollector](https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/TaxCollector.sol#L554) contract, the value of [coinBalance(receiver) is an uint](https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/SAFEEngine.sol#L103). This is cast to an `int` and then negated. However, since `uint` can store higher values than `int`, it is possible that casting from `uint` to `int` may create an overflow.

Consider verifying that the value of `coinBalance(receiver)` is within the acceptable range for negative `int` values before casting and negating. Consider using OpenZeppelin’s [SafeCast](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v3.2.0/contracts/utils/SafeCast.sol) contract, which provides functions for safely casting between types.

_**Update:** Fixed in [pull request #76.](https://github.com/reflexer-labs/geb/pull/76/commits/3bd01713bc0497e77741b13694199529639a2d59)_
