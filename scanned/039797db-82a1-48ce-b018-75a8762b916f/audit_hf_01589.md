# [H] Not updating MINT_COUNT_CID and BURN_COUNT_CID

## Summary
Severity: High
Contest weight: 0.5623
Dataset id: 8542
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The GameItems contract provides the mintBatch and burnBatch functions for batch minting and burning of game items.
```solidity
function mintBatch(
address to,
uint256[] memory ids,
uint256[] memory amounts,
bytes memory data
) external onlyRole(MINTER_ROLE) whenNotPaused {
_mintBatch(to, ids, amounts, data);
}

function mintBatch(
address to,
uint256[] memory ids,
uint256[] memory amounts
) external onlyRole(MINTER_ROLE) whenNotPaused {
_mintBatch(to, ids, amounts, "");
}

function burnBatch(
address from,
uint256[] memory ids,
uint256[] memory amounts
) external onlyRole(GAME_LOGIC_CONTRACT_ROLE) whenNotPaused {
_burnBatch(from, ids, amounts);
}
```
However, during the batch processing, the MINT_COUNT_CID and BURN_COUNT_CID are not updated, which will lead to incorrect supply calculations.

## Recommendation
The logic to handle MINT_COUNT_CID and BURN_COUNT_CID in batch operations should be added.
