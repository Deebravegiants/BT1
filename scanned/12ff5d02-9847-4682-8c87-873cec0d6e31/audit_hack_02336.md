# [M] \[M08\] Not using SafeMath functions

## Summary
Severity: Medium
Source: https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/GlobalSettlement.sol#L298
Type: audit-issue

## Details
There are several places in the code base where regular Solidity arithmetic operators are used. For example:

* In [line 298 of the GlobalSettlement contract](https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/GlobalSettlement.sol#L298) `/` is used.
* In [line 196 of the Coin contract](https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/Coin.sol#L196) `++` is used.
* In [line 565 of the TaxCollector contract](https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/TaxCollector.sol#L565) `/` is used.

These operators do not protect against overflows, underflows or division by `0` and may silently fail or return unexpected values.  
Consider always performing arithmetic operations with functions that protect the code from such scenarios, like the [math libraries of OpenZeppelin contracts](https://github.com/OpenZeppelin/openzeppelin-contracts/tree/release-v3.2.0/contracts/math).

_**Update:** Acknowledged, and will not fix. Reflexer Labs’ statement for this issue:_

> We understand the concern although we would like to stick to the same functions used in MCD
