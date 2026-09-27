# [M] reentrancy-no-eth

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-14
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/15
Type: code-finding

## Details
# Handle

heiho1


# Vulnerability details

## Impact

Function RCMarket#lockMarket() is public and so can be invoked by anyone.  It claims to be called within the context of the autoLock modifier but said modifier is not applied to the function call and so this function can be repeatedly called publicly by anyone.  This could be quite expensive an operation as it collects all rent , change market state, and iterates over all cards for card transfers.  In short it appears this function could cause market misbehavior simply by repeatedly invoking it within a block.

## Proof of Concept

https://github.com/code-423n4/2021-06-realitycards/blob/86a816abb058cc0ed9b6f5c4a8ad146f22b8034c/contracts/RCMarket.sol#L441

## Tools Used

Slither

## Recommended Mitigation Steps

It appears this market should either be restricted to admin/owner access or marked internal and be applied by the modifier.
