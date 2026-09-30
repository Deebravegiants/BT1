# [C] The logic in elapsedTime is flawed

## Summary
Severity: Critical
Contest weight: 0.0630
Dataset id: 14820
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are multiple flaws with the elapsedTime method:
1. If there are 0 windows, the windowIndex variable (which is used for the windows count) will be 1, which is wrong and will lead to a big value for windowElapsedTime when it should be 0
2. If auctionElapsedTime == windowElapsedTime we will get auctionElapsedTime as a result, but if there was just 1 more second in auctionElapsedTime we would get auctionElapsedTime - windowElapsedTime which would be 1 as a result, so totally different result
3. When a window is active, the timestamp argument will have the same value as the auction.startTimestamp so auctionElapsedTime will always be 0 in this case
The method has multiple flaws and works only in the happy-case scenario.

## Recommendation
Remove the method altogether or extract two methods out of it, removing the timestamp parameter to simplify the logic. Also think about the edge case scenarios.
