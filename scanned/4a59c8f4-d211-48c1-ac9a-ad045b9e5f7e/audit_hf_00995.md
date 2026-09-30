# [M] Point.position is not updated for stack slots in _removeStackPosition

## Summary
Severity: Medium
Contest weight: 0.0893
Dataset id: 3212
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In _createLien, when a new stack slot is created, the newSlot.point.position is set to uint8(params.stack.length) which would be its index in the stack. When _removeStackPosition is called to remove a slot from the stack at index position, the newStack[i].point.position is not updated for indexes that are greater than position in the original stack. Also slot.point.position is only used when we emit AddLien and LienStackUpdated events. In both of those cases, we could have used params.stack.length

## Recommendation
If it is necessary to keep slot.point.position due to future upgrades, make sure to update _removeStackPosition so that it updates the positions as well. Otherwise, slot.point.position can be removed.
