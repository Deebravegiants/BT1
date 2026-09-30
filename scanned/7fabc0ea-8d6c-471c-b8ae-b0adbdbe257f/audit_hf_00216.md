# [M] `MovingAverage.setSampleMemory

## Summary
Severity: Medium
Contest weight: 0.4273
Dataset id: 1119
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function setSampleMemory(uint256 _sampleMemory)
    external
    onlyRole(ADMIN_ROLE, "Must have admin privs")
{
    require(_sampleMemory > 0, "Cannot have sample memroy of 0");

    if (_sampleMemory > sampleMemory) {
        for (uint i = sampleMemory; i < _sampleMemory; i++) {
            samples.push();
        }
        counter = counter % _sampleMemory;
    } else {
        activeSamples = _sampleMemory;

        // TODO handle when list is smaller Tue 21 Sep 2021 22:29:41 BST
    }

    sampleMemory = _sampleMemory;
}
```

In the current implementation, when `sampleMemory` is updated, the samples index will be malposition, making `getValueWithLookback()` get the wrong samples, so that returns the wrong value.

## Proof of Concept
* When initial sampleMemory is `10`
  * After `movingAverage.update(1e18)` being called for 120 times
  * The admin calls `movingAverage.setSampleMemory(118)` and set sampleMemory to `118`

The current `movingAverage.getValueWithLookback(sampleLength * 10)` returns `0.00000203312 e18`, while it’s expeceted to be `1e18`

After `setSampleMemory()`, `getValueWithLookback()` may also return `0`or revert FullMath: FULLDIV_OVERFLOW at L134.

## Recommendation
No recommendation
