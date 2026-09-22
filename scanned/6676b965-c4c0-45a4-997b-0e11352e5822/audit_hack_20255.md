# [M] 5.2.3 Old quests can be extended viaincreaseQuestDuration().

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** QuestBoard.sol#L380-L

**Description:** FunctionincreaseQuestDuration()does not check if a quest is already in the past. Extending a
quest from the past in duration is probably not useful. It also might require additional calls toclosePartOfQuest-
Period().

```
function increaseQuestDuration(...) ... {
updatePeriod();
```
```
uint256 lastPeriod = questPeriods[questID][questPeriods[questID].length - 1];
```
```
uint256 periodIterator = ((lastPeriod + WEEK) / WEEK) * WEEK;
```
```
for(uint256 i = 0; i < addedDuration;){
```
```
periodsByQuest[questID][periodIterator]....= ...
periodIterator = ((periodIterator + WEEK) / WEEK) * WEEK;
unchecked{ ++i; }
}
```
```
}
```
**Recommendation:** Determine what the actions should be when the quest is in the past.

**Paladin:** We check that when calling the function, the current period is either the last period of the Quest, or before
that last period. If not, the Quest is over, and we revert. Implemented in #8.

**Spearbit:** Acknowledged.
