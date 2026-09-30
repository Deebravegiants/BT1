# [C] C-07 | User Remains Position Contributor

## Summary
Severity: Critical
Contest weight: 0.2927
Dataset id: 2408
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users are never removed from positionContributors set upon cancellation of their order. This leads to the following scenario:
(1) User creates an order, position count is 1.
(2) User cancels the order, position count is 0 after userPositionKeys is cleared, but user remains a position contributor for that position key in mapping positionContributors.
(3) User creates the same order. Because the user is already seen as a position contributor, the position key is not added to userPositionKeys and the position is not registered for the user, hence their position count remains 0. This impacts most view functions and cancelBatchOrders which directly rely on userPositionKeys.
(4) If the user were to attempt to cancel their "unregistered" order to retrieve their funds, there would be a revert when attempting to remove the tick range, as it does not exist. This is because the "ghost" position was never cleared, hence a new tick range was not inserted upon order creation in step (3). Specifically, an underflow revert on uint256 right = positionTickRangeList[poolId].length - 1; within function findPositionTickRangeIdx will occur. Ultimately, a user who creates the same order after cancelling a previous order loses their funds.

## Proof of Concept
https://github.com/GuardianOrg/univ4-limit-order-hook-team2/pull/2

## Recommendation
Ensure upon cancellation that a user is removed as a position contributor as necessary and that the position key is marked as inactive.
