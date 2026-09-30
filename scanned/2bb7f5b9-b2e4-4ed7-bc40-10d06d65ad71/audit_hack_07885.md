# [M] Periphery.sol: dangerous payable functions

## Summary
Severity: Medium
Reporter: w42d3n
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Periphery.sol: dangerous payable functions

## Summary

## Vulnerability Detail

The contract Periphery.sol use several payable functions:

L116	function sponsorSeries(

L178	function swapForPTs(

L325	function addLiquidity(

In these functions , users can send ETH mistakenly so, we should check the msg.value is 0 or not.


## Impact

Lost of funds for users

## Code Snippet

## Tool used

Manual Review

## Recommendation

add the check for the non-native transfer section as follow

```solidity
require(msg.value == 0,"NON ETH");
```
