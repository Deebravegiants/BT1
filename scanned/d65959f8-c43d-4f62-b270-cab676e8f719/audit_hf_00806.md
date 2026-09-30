# [M] M-07 | Same Heartbeat Assumed For All Price Feeds

## Summary
Severity: Medium
Contest weight: 0.0477
Dataset id: 2542
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The same heartbeat (one hour) is assumed for all chainlink price feeds, but there are assets with different heartbeats for example 24 hours this will result in all operations with a 24-hour heartbeat asset to only work 1 hour a day and DoS the rest of the time.

## Recommendation
Implement the possibility to set the heartbeat for each price feed individually.
