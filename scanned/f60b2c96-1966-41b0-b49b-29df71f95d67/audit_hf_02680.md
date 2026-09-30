# [H] Incorrect Computation Of claimIntervalsPassed

## Summary
Severity: High
Contest weight: 0.7239
Dataset id: 14493
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Intervals since last claim period are incorrectly computed.
Currently, the interval start time is divided by claim interval duration, and subtracted from current block timestamp:
```solidity
return block.timestamp - (getClaimIntervalTimeStart() / getClaimIntervalTime())
```
However, it should actually be the difference between current block’s timestamp and claim interval start, divided by the interval duration.

## Recommendation
Modify code on line [79] to correctly calculate intervals since last claim period, i.e.
```solidity
return (block.timestamp - getClaimIntervalTimeStart()) / getClaimIntervalTime()
```
