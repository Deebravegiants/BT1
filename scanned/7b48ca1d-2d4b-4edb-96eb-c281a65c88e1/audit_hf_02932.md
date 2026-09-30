# [H] Raffles cannot be created

## Summary
Severity: High
Contest weight: 0.7207
Dataset id: 16278
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Similar to C-06 in solidity you cannot add elements to an array by assigning that index:
```solidity
raffles[raffleCounter - 1] = raffle(
    raffleCounter,
    _raffleName,
    _rewardAmount,
    block.timestamp,
    _endTime,
    _price,
    0,
    _image
);
```
This causes an array out-of-bounds panic.

## Recommendation
We recommend you change to use push:
```solidity
// - raffles[raffleCounter - 1] = raffle(
raffles.push(raffle(
    raffleCounter,
    _raffleName,
    _rewardAmount,
    block.timestamp,
    _endTime,
    _price,
    _image
// - );
));
raffleCounter++;
```
Varonve.md
