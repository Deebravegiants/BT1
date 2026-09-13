# [M] Fairswap interfaces are inconsistent

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

There are unexpected inconsistencies between the three Fairswap contract interfaces, which may cause issues for composability with external contracts. 

#### Examples

The function used to submit orders between the base and settlement currency has a different name across the three exchanges: 

1. In `Fairswap_iDOLvsETH` it is called: `orderEThToToken()`.
2. In `Fairswap_iDOLvsLien` it is called: `OrderBaseToSettlement()` (capitalized).
3. In `Fairswap_iDOLvsImmmortalOptions` it is called: `orderBaseToSettlement()`.

#### Recommendation

Implement the desired interface in a separate file, and inherit it on the exchange contracts to ensure they are implemented as intended.
