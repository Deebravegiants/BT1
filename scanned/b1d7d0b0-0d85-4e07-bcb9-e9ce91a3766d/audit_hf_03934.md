# [M] Market: DoS when stuffed with pending pro- tected position updates

## Summary
Severity: Medium
Contest weight: 0.5944
Dataset id: 20251
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In _invariant, there is a limit on the number of pending position updates. But for protected position updates, _invariant returns early and does not trigger this check.
```solidity
function _invariant(
    Context memory context,
    address account,
    Order memory newOrder,
    bool protected
) private view {
    ....
    if (protected) return; // The following invariants do not apply to protected position updates (liquidations)
    ....
    if (
        context.global.currentId > context.global.latestId + context.marketParameter.maxPendingGlobal ||
        context.local.currentId > context.local.latestId + context.marketParameter.maxPendingLocal
    ) revert MarketExceedsPendingIdLimitError();
    ....
}
```
After the _invariant check, the position updates will be added into pending position queues.
```solidity
_invariant(context, account, newOrder, collateral, protected);
// store
_pendingPosition[context.global.currentId].store(context.currentPosition.global);
_pendingPositions[account][context.local.currentId].store(context.currentPosition.local);
```
When the protocol enters next oracle version, the global pending queue _pendingPosition will be settled in a loop.
```solidity
function _settle(Context memory context, address account) private {
    ....
    // settle
    while (
        context.global.currentId != context.global.latestId &&
        (nextPosition = _pendingPosition[context.global.latestId + 1].read()).ready(context.latestVersion)
    ) _processPositionGlobal(context, context.global.latestId + 1, nextPosition);
```
The OOG revert happens if there are too many pending position updates.
This revert will happen on every update calls because they all need to settle this _pendingPosition before update.
```solidity
function update(
    address account,
    bool protect
) external nonReentrant whenNotPaused {
    Context memory context = _loadContext(account);
    _settle(context, account);
    _update(context, account, newMaker, newLong, newShort, collateral, protect);
    _saveContext(context, account);
}
```
The protocol will be fully unfunctional and funds will be locked. There will be no recover to this DoS.
A malicious user can trigger this intentionally at very low cost. Alternatively, this can occur during a volatile market period when there are massive liquidations.

## Recommendation
Either or both,
1. Limit the number of pending protected position updates can be queued in _invariant.
2. Limit the number of global pending protected positions can be settled in _settle.
