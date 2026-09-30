# [M] Add extra 0 checks in verifyAggregateRoot() and proveMessageRoot()

## Summary
Severity: Medium
Contest weight: 0.5507
Dataset id: 6832
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The functions verifyAggregateRoot() and proveMessageRoot() verify and confirm roots. A root value of 0 is a special case. If this value would be allowed, then the functions could allow invalid roots to be passed.
Currently the functions verifyAggregateRoot() and proveMessageRoot() don't explicitly verify the roots are not 0.

```solidity
function verifyAggregateRoot(bytes32 _aggregateRoot) internal {
    if (provenAggregateRoots[_aggregateRoot]) {
        return;
    }
    ... // do several verifications
    provenAggregateRoots[_aggregateRoot] = true;
    ...
}
```

```solidity
function proveMessageRoot(...) ... {
    if (provenMessageRoots[_messageRoot]) {
        return;
    }
    ... // do several verifications
    provenMessageRoots[_messageRoot] = true;
}
```

## Recommendation
As an extra safety precaution do the following:
• In function verifyAggregateRoot() check _aggregateRoot != 0.
• In proveMessageRoot() check _messageRoot != 0.
