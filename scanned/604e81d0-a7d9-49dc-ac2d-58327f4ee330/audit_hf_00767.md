# [C] C-04 | Limit Orders Missed Due

## Summary
Severity: Critical
Contest weight: 0.2319
Dataset id: 2387
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _ﬁndOverlappingPositions function the search for executable orders is halted as soon as a position is encountered which has an end tick after the resulting pool price and is therefore unexecutable.
However, for zeroForOne limit orders, since the positionTickRangeList is sorted by the bottom tick this results in orders often being skipped when they are in fact executable.
Consider the following sorted positionTickRangeList.
0: Position(lower: 60, 300)
1: Position(lower: 120, 360)
2: Position(lower: 180, 300)
When the pool price swaps to tick 320 the loop in the _ﬁndOverlappingPositions function will break because the order in the ﬁrst index has a top tick which is above the resulting pool price. However the subsequent order in index 2 should have been included in the positionsId list and executed.

## Proof of Concept
https://gist.github.com/GuardianAudits/91e45729f439d52f8addbe3d5d736004

## Recommendation
Consider implementing a combination of a bitmap to show ticks which are the end tick for at least one order in the Gamma system and a mapping from tick to a set of positions which end at that tick.
