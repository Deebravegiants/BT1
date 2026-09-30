# [M] M-01 | MarketMaking Ignores Loops Capacity

## Summary
Severity: Medium
Contest weight: 0.0492
Dataset id: 21901
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Additional debt can now serve as capacity for the Baseline system in the Loops vault. This is accounted for in the CreditFacility but not in the MarketMaking contract. As a result the capacity checks between the CreditFacility and MarketMaking policies will not agree.

## Recommendation
Include the LOOPS.totalDebt() when computing the capacity in the MarketMaking contract.
