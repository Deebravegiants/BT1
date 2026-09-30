# [H] The executeVirtualOrdersToBlock function updates the oracle with the wrong block.number

## Summary
Severity: High
Contest weight: 0.1352
Dataset id: 6973
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The executeVirtualOrdersToBlock is external, meaning anyone can call this function to execute virtual orders.
The _maxBlock parameter can be lower block.number which will make the oracle malfunction as the oracle update function _updateOracle uses the block.timestamp and assumes that the update was called with the reserves at the current block.
This will make the oracle update with an incorrect value when _maxBlock can be lower than block.number.

## Recommendation
Consider adding the block number as a parameter within the _updateOracle in order for this function to not rely on the current block.
