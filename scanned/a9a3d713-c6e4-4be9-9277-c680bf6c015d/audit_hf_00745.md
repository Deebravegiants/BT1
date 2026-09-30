# [M] M-09 | Disputer Cannot Re-Dispute After Reset

## Summary
Severity: Medium
Contest weight: 0.0897
Dataset id: 2302
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a market is reset following multiple active disputes, a user whose dispute is still considered
“open” cannot reclaim their bond because the system only allows bond retrieval after the market is
finalized.
As a result, that user remains in a state with an unclaimed (open) dispute bond, which prevents them
from initiating a new dispute on a subsequent outcome proposal. This essentially locks them out of
further participation in the dispute process for that market.

## Recommendation
Enable retrieval or reusability of the bond upon a market reset for disputes that remain open.
Specifically, consider allowing users to claim or “migrate” their open dispute bond once the market
transitions to a reset state—rather than strictly requiring the market to be finalized.
