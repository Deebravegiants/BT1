# [H] Timestamp of the answers should be signed by validators and checked on-chain

## Summary
Severity: High
Contest weight: 0.1531
Dataset id: 17422
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Answers submitted by validators could be stale, but are still aggregated and considered to be a fresh price dated at block.timestamp. There could be a significant time delay from the time signers submitted their answers to the time that the transmit transaction is executed (Eg. function caller withholds the transaction, network congestion etc.). There is no guarantee on the freshness of data as a result. Stale prices will affect protocol integrations significantly, especially money markets, as can be seen in the recent incident with LUNA.

## Recommendation
Include the timestamp as part of the data to be signed by validators, and check against block.timestamp.
