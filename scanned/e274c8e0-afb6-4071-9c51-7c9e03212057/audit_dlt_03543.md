# [M] Liquidity Cap changes for active pools affect winning odds unexpectedly

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-pooltogether
Published: 2021-06-23
Source: https://github.com/code-423n4/2021-06-pooltogether-findings/issues/56
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

Liquidity cap is useful for a guarded launch where the project gradually increases the pool cap to mitigate newly launched project risks. However, the amount of deposits for this particular protocol has a direct impact on a user's odds of winning (depending on the prizing strategy) unlike other protocols. Winning odds for users continuously changes depending on the amount of deposits but the worst case odds can be estimated based on the liquidity cap. But if that increases significantly then users’ estimates at deposit time will be incorrect and overestimated. Given that fairness is a key value proposition for this protocol to function transparently, the ability to increase the liquidity cap by a potentially untrustworthy owner negatively affects that aspect.

Impact: If a malicious pool owner increases the cap significantly once the pool is active, the winning odds of previously deposited users is impacted negatively and unexpectedly if new users (potentially owner’s sybils) make large deposits.

## Proof of Concept

Scenario: Alice deposits 1K DAI into a pool with a cap of 10K, estimating her winning chances as 10%. Malicious pool owner Mallory increases the cap to 100K reducing Alice’s odds to 1%.

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/PrizePool.sol#L977-L986

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/PrizePool.sol#L1069-L1072


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

The benefits of a guarded launch for pool cap has to be evaluated against the concerns pointed out here. 1) Consider a timelocked increase of pool cap which allows users to withdraw deposits if the new cap, which only takes effect after the timelocked period, seems too large. 2) Consider a hardcoded max cap as a percentage of the initial cap beyond which the owner cannot increase it and gives the users an estimate of the worst case cap for their odds.
