# [M] M-01 | MintUSD() Does Not Verify Market Capacities

## Summary
Severity: Medium
Contest weight: 0.0601
Dataset id: 22102
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The mintUsd() function decreases the creditCapacity of the markets connected to the pool.
However, it does not verify if there is enough creditCapacity available to support the markets. As a
result, by using mintUsd, LPs can potentially push the markets below their minimumCredit.

## Recommendation
Similar to the practice in delegateCollateral(), the addition of the _verifyNotCapacityLocked() check
to mintUsd() is suggested. This measure will prevent the minting of USD if there will be locked
markets as a consequence of minting.
