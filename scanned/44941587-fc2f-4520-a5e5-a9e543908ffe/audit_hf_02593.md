# [M] RLQ-1 | Ineﬃcient Reward Design

## Summary
Severity: Medium
Contest weight: 0.0926
Dataset id: 13966
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If userA has their funds deposited but does not call updatePosition for a significant period of time, the next time they update their position they receive rewards based on the level of their position the last time it was updated. In this case userA earns less than userB, who regularly calls updatePosition as soon as their relic’s maturity reaches the next level and therefore received more rewards at the higher levels.

## Recommendation
If this is not desired behavior, consider evaluating the current level of the user’s relic in _updatePosition for distributing rewards, therefore removing the need to call updatePosition regularly. If this approach is taken, consider introducing logic that prevents users from simply holding their positions to receive all of their rewards based on a higher level, when in reality a portion of those rewards should have been weighted at a lower level.
