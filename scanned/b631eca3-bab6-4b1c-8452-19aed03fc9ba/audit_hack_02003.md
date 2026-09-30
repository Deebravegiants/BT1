# [M] 7.5 View Functions Reentrancy

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

Some view functions don't use the _viewlock_ modifier. In case of reentrancy due to ERC20 token
calls (e.g. ERC777), these getters can return unreliable data. This may break the integration with other
contracts and systems that rely on these getters. Such getter functions are:


- getAmountOutGivenInMMM

Please note, this list might be incomplete. Any function of a contract that does external call need to be
lock or viewlock protected, if other external contract might rely on the data from this contract, such as
spot prices, weights, etc.

Code corrected:

View locks have been added to all view functions in the Pool.sol contract.
