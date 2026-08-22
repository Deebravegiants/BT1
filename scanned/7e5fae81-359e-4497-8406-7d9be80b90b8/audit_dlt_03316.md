# [M] Lack of sufficient power check in `updateValset` of `Gravity`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-08
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/63
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

The `updateValset` function does not check whether the new valset has sufficient power to pass a vote (see the `constructor` for more details). If the new valset does not, any function calling `checkValidatorSignatures` will be disabled (since the transaction reverts).

## Proof of Concept

Referenced code:
[Gravity.sol#L224](https://github.com/althea-net/cosmos-gravity-bridge/blob/92d0e12cea813305e6472851beeb80bd2eaf858d/solidity/contracts/Gravity.sol#L224)
[Gravity.sol#L584-L590](https://github.com/althea-net/cosmos-gravity-bridge/blob/92d0e12cea813305e6472851beeb80bd2eaf858d/solidity/contracts/Gravity.sol#L584-L590)

## Recommended Mitigation Steps

Add a check to ensure that the total power of the new valset is at least the power threshold.
