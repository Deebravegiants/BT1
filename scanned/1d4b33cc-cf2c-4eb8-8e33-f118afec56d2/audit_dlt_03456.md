# [M] Incorrect parameters passed while adding new staking fund

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-floatcapital
Published: 2021-08-11
Source: https://github.com/code-423n4/2021-08-floatcapital-findings/issues/139
Type: code-finding

## Details
# Handle

hack3r-0m


# Vulnerability details

https://github.com/hack3r-0m/2021-08-floatcapital/blob/main/contracts/contracts/LongShort.sol#L363-L365

`initializeMarket` can be called with different `marketIndex` each time while calling `IStaker(staker).addNewStakingFund` with the same parameters resulting in overriding of mapping in the staker contract and hence removing past staking funds.

`latestMarket` should be replaced with `marketIndex` in the above-marked code lines.
