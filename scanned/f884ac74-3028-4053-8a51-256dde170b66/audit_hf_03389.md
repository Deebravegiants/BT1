# [M] SWOU-1 | LimitSwaps Unnecessarily Delayed

## Summary
Severity: Medium
Contest weight: 0.0732
Dataset id: 18497
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The validateOracleBlockNumbers function for LimitSwaps does not allow oracle block numbers to
be equal to the orderUpdatedAtBlock. This is in contradiction to the oracle block validation for
increase and decrease orders.
Additionally, this unnecessarily requires that limit swaps be executed at a delayed block number,
when the current block number may provide a more favorable execution for the trader.

## Recommendation
Change the requirement from !minOracleBlockNumbers.areGreaterThan(orderUpdatedAtBlock) to
!minOracleBlockNumbers.areGreaterThanOrEqualTo(orderUpdatedAtBlock).
