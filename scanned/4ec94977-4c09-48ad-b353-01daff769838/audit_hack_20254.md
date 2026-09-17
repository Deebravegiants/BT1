# [M] 5.2.2 UpdatingQuestBoardinMultiMerkleDistributor.solwill not work

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** MultiMerkleDistributor.sol#L285-L

**Description:** UpdatingQuestManager/QuestBoardinMultiMerkleDistributor.solwill give the following issue:

If thenewQuestBoarduses the current implementation ofQuestBoard.sol, it will start withquestId == 0again,
thus attempting to overwrite previous quests.

```
function updateQuestManager(address newQuestBoard) external onlyOwner {
questBoard = newQuestBoard;
}
```
**Recommendation:** Confirm the usefulness of updating theQuestManager/QuestBoard. If this functionality is
relevant, adaptQuestBoard.solto start with a higher value fornextID.

**Paladin:** TheQuestBoardshould be unique (only replaced if the GaugeController is replaced or in case of a bug
requiring to kill the contract), while the Distributor could be replaced to propose new ways to redeem the reward
tokens.

QuestBoardis now immutable, therefore this method is not needed anymore.

Implemented in #16.

**Spearbit:** Acknowledged.
