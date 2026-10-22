# [H] lastUpdatedDay not initialized

## Summary
Severity: High
Contest weight: 0.1698
Dataset id: 236
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The variable lastUpdatedDay in IncentiveDistribution.sol is not (properly) initialized. This means the function updateDayTotals will end up in a very large loop which will lead to an out of gas error. Even if the loop would end, the variable currentDailyDistribution would be updated very often. Thus updateDayTotals cannot be performed.

The entire IncentiveDistribution does not work. If the loop would stop, the variable currentDailyDistribution is not accurate, resulting in a far lower incentive distribution than expected.

Recommend initializing lastUpdatedDay with something like block.timestamp / (1 days)

    uint256 lastUpdatedDay; # ==> lastUpdatedDay = 0

## Recommendation
No recommendation
