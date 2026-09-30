# [M] OOG error in clearLoop()

## Summary
Severity: Medium
Contest weight: 0.0965
Dataset id: 13801
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function ResetClearLoopSubsystem.clearLoop() calls PointsMap.clear(empire) to clear all utilities associated with an empire. The issue is that this function loops through all players of the empire and clears their data and if the player's count is very big then the execution can encounter OOG. function clear(EEmpire empire) internal { bytes32[] memory players = keys(empire); for (uint256 i = 0; i < players.length; i++) { Value_PointsMap.deleteRecord(empire, players[i]); Meta_PointsMap.deleteRecord(empire, players[i]); Keys_PointsMap.deleteRecord(empire); } Empire.setPointsIssued(empire, 0); }

## Recommendation
Add restriction to the number of players or avoid looping through all of them in one transaction.
