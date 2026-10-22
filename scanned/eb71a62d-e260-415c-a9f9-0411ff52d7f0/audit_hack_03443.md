# [M] Should prevent users from sending more native tokens in the buyPosition function

## Summary
Severity: Medium
Reporter: Bnke0x0
Source: https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L492
Type: audit-issue

## Details
# Should prevent users from sending more native tokens in the buyPosition function

## Summary

## Vulnerability Detail

## Impact
When a user bridges a native token via the buyPosition function of BvbProtocol, the contract checks msg.value >= sellOrder.price holds. 

## Code Snippet
https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L492

         'require(msg.value >= sellOrder.price, "INVALID_ETH_VALUE");'

## Tool used

Manual Review

## Recommendation
Consider changing `>=` to `==` at line 492.
