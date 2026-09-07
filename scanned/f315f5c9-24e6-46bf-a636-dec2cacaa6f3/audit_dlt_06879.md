# [H] lastUpdatedDay not initialized

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-marginswap
Published: 2021-04-04
Source: https://github.com/code-423n4/2021-04-marginswap-findings/issues/14
Type: code-finding

## Details
# Email address

mail@gpersoon.com


# Handle

gpersoon


# Eth address

gpersoon.eth


# Vulnerability details

The variable lastUpdatedDay in IncentiveDistribution.sol is not (properly) initialized.
This means the function updateDayTotals will end up in a very large loop which will lead to an out of gas error.
Even if the loop would end, the variable currentDailyDistribution would be updated very often.
Thus updateDayTotals cannot be performed 


# Impact

The entire IncentiveDistribution does not work.
If the loop would stop, the variable currentDailyDistribution is not accurate, resulting in a far lower incentive distribution than expected.


# Recommended mitigation steps

Initialize lastUpdatedDay with something like block.timestamp / (1 days)


# Proof of concept

uint256 lastUpdatedDay; # ==> lastUpdatedDay = 0


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-04-marginswap-findings/issues/14_
