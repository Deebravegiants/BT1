# [M] Updating QuestBoard in MultiMerkleDistributor.sol will not work

## Summary
Severity: Medium
Contest weight: 0.0663
Dataset id: 11317
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Updating QuestManager/ QuestBoard in MultiMerkleDistributor.sol will give the following issue:
If the newQuestBoard uses the current implementation of QuestBoard.sol, it will start with questId == 0 again, thus attempting to overwrite previous quests.
function updateQuestManager(address newQuestBoard) external onlyOwner {
questBoard = newQuestBoard;
}

## Recommendation
Confirm the usefulness of updating the QuestManager/ QuestBoard. If this functionality is relevant, adapt QuestBoard.sol to start with a higher value for nextID.
