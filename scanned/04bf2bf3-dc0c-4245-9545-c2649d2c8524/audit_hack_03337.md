# [M] Use `call()` with value instead of `transfer()` on `address payable`

## Summary
Severity: Medium
Reporter: pashov
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L29
Type: audit-issue

## Details
# Use `call()` with value instead of `transfer()` on `address payable`

## Summary
The code makes use of the `transfer()` method on `address payable` which is strongly discouraged
## Vulnerability Detail
The use of the deprecated `transfer()` function for an address will inevitably make the transaction fail when:

1. The claimer smart contract does not implement a payable function.
2. The claimer smart contract does implement a payable fallback which uses more than 2300 gas unit.
3. The claimer smart contract implements a payable fallback function that needs less than 2300 gas units but is called through proxy, raising the call's gas usage above 2300.

Additionally, using higher than 2300 gas might be mandatory for some multisig wallets.
## Impact
This vulnerability can result in a permanent DoS if the receiver address is of the above mentioned types, hence Medium severity

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L29
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L489
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L152
## Tool used

Manual Review

## Recommendation
Use `call()` with value instead.
