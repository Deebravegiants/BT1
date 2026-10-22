# [H] Funds can be stolen because of incorrect update of rollover index

## Summary
Severity: High
Contest weight: 0.2903
Dataset id: 19896
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the case where the owner has an existing rollover, the ownerToRollOverQueueIndex incorrectly updates to the last queue index. This causes the notRollingOver check to be performed on the incorrect _id, which then allows the depositor to withdraw funds that should've been locked.
In enlistInRollover(), if the user has an existing rollover, it overwrites the existing data:
if (ownerToRollOverQueueIndex[_receiver] != 0) {
// if so, update the queue
uint256 index = getRolloverIndex(_receiver);
rolloverQueue[index].assets = _assets;
rolloverQueue[index].epochId = _epochId;
However, regardless of whether the user has an existing rollover, the ownerToRolloverQueueIndex points to the last item in the queue:
ownerToRollOverQueueIndex[_receiver] = rolloverQueue.length;
Thus, the notRollingOver modifier will check the incorrect item for users with existing rollovers:
QueueItem memory item = rolloverQueue[getRolloverIndex(_receiver)];
if (
item.epochId == _epochId &&
(balanceOf(_receiver, _epochId) - item.assets) < _assets
) revert AlreadyRollingOver();
allowing the user to withdraw assets that should've been locked.
Users are able to withdraw assets that should've been locked for rollovers.

## Recommendation
The ownerToRollOverQueueIndex should be pointing to the last item in the queue in the else case only: when the user does not have an existing rollover queue item.
} else {
// if not, add to queue
rolloverQueue.push(
QueueItem({
assets: _assets,
receiver: _receiver,
epochId: _epochId
})
);
+ ownerToRollOverQueueIndex[_receiver] = rolloverQueue.length;
}
- ownerToRollOverQueueIndex[_receiver] = rolloverQueue.length;
