# [M] OPMAN-1 | Risk Of DoS

## Summary
Severity: Medium
Contest weight: 0.0891
Dataset id: 19356
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _futuresTradeUploadData function, a batch of trades are uploaded in a single transaction which allows a single malicious trade to DoS the entire batch if it reverts. For example, one trade in the batch could have an invalid symbolHash, which would cause the executeProcessValidatedFutures execution to revert. Similarly, in the _eventUploadData function, a batch of events are uploaded to be processed in a single tx which allows a single invalid event to DoS the entire batch.

## Recommendation
Be aware of this DoS risk and be sure to simulate batches to verify that they contain no invalid trades before sending a batch upload transaction. Additionally, consider implementing logic at the contract to handle invalid events or trades.
