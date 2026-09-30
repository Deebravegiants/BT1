# [M] Updating BoardCachedGreeks does not check if a board is expired

## Summary
Severity: Medium
Contest weight: 0.0736
Dataset id: 17459
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A function in the OptionGreekCache contract that updates the cached greeks for an OptionBoardCache misses expiration checks for the board. The _updateBoardCachedGreeks function only checks if the board id is 0 but misses a check if the board is expired. Various parameters of the GlobalCache and the OptionBoardCache can be updated based on the expired board values.

## Recommendation
Include a check that ensures that a board has not expired before the greeks of the OptionBoardCache are updated. This has been resolved. https://github.com/lyra-finance/lyra-protocol/blob/avalon/contracts/OptionGreekCache.sol#L727-L729 Looks reasonable.
