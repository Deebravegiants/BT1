# [M] ORDH-2 | Phantom Decrease

## Summary
Severity: Medium
Contest weight: 0.1046
Dataset id: 16902
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible to have a decrease order in the orderStore when no corresponding position is present because orders are not cancelled upon failure with the EMPTY_POSITION_ERROR_KEY. Consider the following scenario: User A creates a position User A sends a LimitDecreaseOrder and a MarketDecreaseOrder in the same block LimitDecreaseOrder gets executed first MarketDecreaseOrder is now floating on an empty position and it never gets canceled User A opens a new position with an increase order of the same market, collateral token, and directionality The market decrease order unexpectedly affects User A’s new position as it was waiting to be executed in the orderStore

## Recommendation
Cancel the order upon failed execution in the case of EMPTY_POSITION_ERROR_KEY.
