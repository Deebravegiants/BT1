# [M] 5.2.4 Accidental call ofaddQuestcould block contracts

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** MultiMerkleDistributor.sol#L240, QuestBoard.sol#L276-L

**Description:** TheaddQuest()function uses anonlyAllowedaccess control modifier. This modifier checks if
msg.senderisquestBoardorowner. However, theQuestBoard.solcontract has aQuestIDregistration and a
token whitelisting mechanism which should be used in combination withaddQuest()function. Ifowneraccidentally
callsaddQuest(), theQuestBoard.solcontract will not be able to calladdQuest()for thatquestID. As soon as
createQuest()tries to add that samequestIDthe function will revert, becoming uncallable becausenextIDstill
maintains that same value.

```
function createQuest(...) ... {
...
uint256 newQuestID = nextID;
nextID += 1;
...
require(MultiMerkleDistributor(distributor).addQuest(newQuestID, rewardToken), "QuestBoard: Fail
,! add to Distributor");
...
}
```

```
function addQuest(uint256 questID, address token) external onlyAllowed returns(bool) {
require(questRewardToken[questID] == address(0), "MultiMerkle: Quest already listed");
require(token != address(0), "MultiMerkle: Incorrect reward token");
// Add a new Quest using the QuestID, and list the reward token for that Quest
questRewardToken[questID] = token;
emit NewQuest(questID, token);
return true;
}
```
Note: Set to medium risk because the likelihood of this happening is low, but the impact is high.

**Recommendation:** Replace the modifier onaddQuest()to a modifier likeonlyQuestBoard():

```
modifier onlyQuestBoard(){
require(msg.sender == questBoard, "MultiMerkle: Not allowed");
_;
}
```
**Paladin:** Choice to put only a require instead of a 1 time use modifier. Implemented in #5.

**Spearbit:** Acknowledged.
