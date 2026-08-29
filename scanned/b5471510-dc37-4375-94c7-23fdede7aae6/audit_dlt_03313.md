# [H] Function `setAmicableResolution` is susceptible to front-running attacks

## Summary
Severity: High
Chain: Smart contract
Component: 2021-08-realitycards
Published: 2021-08-25
Source: https://github.com/code-423n4/2021-08-realitycards-findings/issues/66
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

The `setAmicableResolution` function in `RCMarket` allows the admin to override the oracle's answer. However, this function is susceptible to front-running attacks where a user could set the winning outcome to the oracle's answer before the admin's transaction is executed, which prevents the admin from changing the outcome to what he desired.

## Proof of Concept

Consider the following scenario:

1. Now the state of the market is `LOCKED`. The oracle is finalized, but the winning outcome is not set yet. 
2. However, the admin wants to override the oracle, so he calls the `setAmicableResolution` function with the winning outcome he desired.
3. A user does not want the oracle to be overridden (perhaps he has an advantage on the oracle's answer), so he front-runs the admin's transactions and calls `getWinnerFromOracle`.
4. The user's transaction is executed, which sets the winning outcome to the oracle's answer. Now the state of the market proceeds to `WITHDRAW`.
5. The admin's transaction thus has no impact on the outcome since the `setWinner` function does nothing when the market state is in `WITHDRAW`. As a result, the admin failed to set the outcome.

Referenced code:
[RCMarket.sol#L438-L444](https://github.com/code-423n4/2021-08-realitycards/blob/main/contracts/RCMarket.sol#L438-L444)

## Recommended Mitigation Steps

Consider modifying the `setWinner` function to allow the admin to change the winning outcome even when the market is in the `WITHDRAW` state. It is even better to force the user to wait for a period of time (e.g., at least a block) before claiming his NFT after the market state changes to `WITHDRAW`.
