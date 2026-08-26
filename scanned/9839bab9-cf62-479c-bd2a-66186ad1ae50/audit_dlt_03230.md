# [M] users might pay enormous amouts of gas

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-timeswap
Published: 2022-01-05
Source: https://github.com/code-423n4/2022-01-timeswap-findings/issues/74
Type: code-finding

## Details
# Handle

danb


# Vulnerability details

https://github.com/code-423n4/2022-01-timeswap/blob/main/Timeswap/Timeswap-V1-Convenience/contracts/libraries/Mint.sol#L141

when a user mints new liquidity, it the pair doesn't already exist, it deploys it.

deploying a new contract on ethereum is super expensive, especially when it's such a large contract like TimeswapPair, it can cost thousands of dollars.

https://medium.com/the-capital/how-much-does-it-cost-to-deploy-a-smart-contract-on-ethereum-11bcd64da1

## Impact
user who try to mint liquidity on pair that doesn't exist will end up paying thousands of dollars.


## Recommended Mitigation Steps
If the pair doesn't exist, revert instead of deploying it.
deploying a new contract should be the user's choice, since it's so expensive.
