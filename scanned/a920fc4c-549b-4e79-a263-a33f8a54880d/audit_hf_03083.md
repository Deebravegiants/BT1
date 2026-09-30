# [M] Duplicate signature should be checked in the first round as well

## Summary
Severity: Medium
Contest weight: 0.0806
Dataset id: 17407
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The duplicate signature check for the first round is skipped. This is partially caused by a mismatch in _roundId and latestAggregatorRoundId. _roundId has to be 0 for the first round, to match latestAggregatorRoundId = 1. However, the duplicate check only occurs when _roundId is greater than zero. Thus, the check is skipped for the first round. Duplicate signatures and answers can be submitted for the first round.

## Recommendation
Sync the round ids. Then, the duplicate check signature becomes require(priceFeed.latestRound() + 1 == _roundId, "Wrong roundId");dId This also means that the minimum value of _roundId is 1, resulting in the if (_roundId > 0) condition being redundant.
