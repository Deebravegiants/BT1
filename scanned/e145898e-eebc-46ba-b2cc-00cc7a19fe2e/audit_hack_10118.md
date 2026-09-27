# [M] Matic doent work in this contract

## Summary
Severity: Medium
Reporter: simon135
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Matic doent work in this contract

## Summary
since the contract is using `weth` for wrapping `msg.value` but if it's on a polygon the function will just revert since the deposit is not for regular users. 
## Vulnerability Detail
when `marginTrading` goes live on Polygon,
and a user trying to wrap msg.value into weth, it won't work because the `deposit` function in the normal weth contract is 
## Impact

## Code Snippet
weth contract on polygon
```solidity
   */
    function deposit(address user, bytes calldata depositData)
        external
        override
        only(DEPOSITOR_ROLE)
```
## Tool used

Manual Review

## Recommendation
don't use weth and have some sort of other function wrap native tokens  function for each chain.
