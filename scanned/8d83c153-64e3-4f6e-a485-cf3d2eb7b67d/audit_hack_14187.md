# [M] Many functions lack `non-reentrant` modifier

## Summary
Severity: Medium
Reporter: Joyous Heather Bobcat
Source: https://github.com/sherlock-audit/2023-06-tokemak/blob/main/v2-core-audit-2023-07-14/src/destinations/adapters/BalancerBeethovenAdapter.sol#L88
Type: audit-issue

## Details
# Many functions lack `non-reentrant` modifier
## Summary

Many functions inside this protocol lack `non-reentrant` modifier which maybe cause reentrancy vulnerability.

## Vulnerability Detail

Currently, many functions lack `non-reentrant` modifier, these functions may cause reentrancy vulnerability, includes
BalancerBeethovenAdapter, CurveV2FactoryCryptoAdapter and MaverickAdapter contracts.


## Impact

Maybe get reentrancy vulnerability.


## Code Snippet

https://github.com/sherlock-audit/2023-06-tokemak/blob/main/v2-core-audit-2023-07-14/src/destinations/adapters/BalancerBeethovenAdapter.sol#L88

https://github.com/sherlock-audit/2023-06-tokemak/blob/main/v2-core-audit-2023-07-14/src/destinations/adapters/BalancerBeethovenAdapter.sol#L151

https://github.com/sherlock-audit/2023-06-tokemak/blob/main/v2-core-audit-2023-07-14/src/destinations/adapters/BalancerBeethovenAdapter.sol#L198

https://github.com/sherlock-audit/2023-06-tokemak/blob/main/v2-core-audit-2023-07-14/src/destinations/adapters/BalancerBeethovenAdapter.sol#L229

https://github.com/sherlock-audit/2023-06-tokemak/blob/main/v2-core-audit-2023-07-14/src/destinations/adapters/MaverickAdapter.sol#L72

https://github.com/sherlock-audit/2023-06-tokemak/blob/main/v2-core-audit-2023-07-14/src/destinations/adapters/MaverickAdapter.sol#L131


## Tool used

Manual Review

## Recommendation

Add `non-reentrant` modifier to these functions.
