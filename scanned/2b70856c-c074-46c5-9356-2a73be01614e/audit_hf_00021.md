# [M] DIEM-7 | Borrowing Fees Extend Past Option Expiry

## Summary
Severity: Medium
Contest weight: 0.0916
Dataset id: 97
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a trader closes a trade their borrowing fees are computed based on the period from the trade.timestamp to the current block.timestamp. However, when an option expires the trader will be closing the trade at a timestamp that is past the expiry time of the option. Therefore borrowing fees accrue for the option even past it’s expiry, when the result has already settled and cannot change. The segment of time between the option expiry and the timestamp of the block in which the trader closes the trade should not be factored when the borrowing fees are computed.

## Recommendation
Compute borrowing fees for the period where the option was tradeable and not expired.
