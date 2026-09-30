# [M] Function _getParentBlockRoot() limits the beacon roots lookback window

## Summary
Severity: Medium
Contest weight: 0.3817
Dataset id: 13973
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Since timestamps are 12 seconds apart, the check on line L384 should be block.timestamp - timestamp >= Constants.BEACON_ROOTS_RING_BUFFER * 12.
Currently, this would limit the _getParentBlockRoot() to return only 683 of the latest stored beacon block roots, while the beacon roots contract accommodates 8191.

## Recommendation
Change the code on line 384 to Constants.BEACON_ROOTS_RING_BUFFER * 12.
The check could also be entirely removed since the beacon roots contract will also revert on a query that is more than 8191 roots old.
```solidity
# Pseudo code of the beacon roots contract
def get():
    if len(evm.calldata) != 32:
        evm.revert()
    if to_uint256_be(evm.calldata) == 0:
        evm.revert()
    timestamp_idx = to_uint256_be(evm.calldata) % HISTORY_BUFFER_LENGTH
    timestamp = storage.get(timestamp_idx)
    if timestamp != evm.calldata:
        evm.revert()
    root_idx = timestamp_idx + HISTORY_BUFFER_LENGTH
    root = storage.get(root_idx)
    evm.return(root)
```
