# [C] 5.1.5 CallingfindCheckpointHints()with_firstIndexas 0 will always revert

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk

**Context:** LidoYieldProvider.sol#L93-L

**Description:** LidoYieldProvider.claim()callsfindCheckpointHints()with_firstIndexas 0 :

```
uint256[] memory hintIds = WITHDRAWAL_QUEUE.findCheckpointHints(
requestIds,
0,
WITHDRAWAL_QUEUE.getLastCheckpointIndex()
);
```
However,_firstIndexcannot be 0 since Lido's checkpoint list is 1-indexed, as stated in the documentation here:

```
_firstIndexmust be greater than 0, because checkpoint list is 1-based array
```
findCheckpointHints()will revert in this check:

```
if (_start == 0 || _end > lastCheckpointIndex) revert InvalidRequestIdRange(_start, _end);
```

# DRAFT

This will cause all withdrawals from Lido to be unclaimable.

**Recommendation:** CallsfindCheckpointHints()with_firstIndexas 1 :

```
uint256[] memory hintIds = WITHDRAWAL_QUEUE.findCheckpointHints(
requestIds,
```
- 0,
+ 1,
    WITHDRAWAL_QUEUE.getLastCheckpointIndex()
);
