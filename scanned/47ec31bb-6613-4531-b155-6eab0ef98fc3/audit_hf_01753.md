# [M] FeeCollector not well integrated

## Summary
Severity: Medium
Contest weight: 0.3941
Dataset id: 9627
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
There is a contract to pay fees for using the bridge: FeeCollector. This is used by crafting a
transaction by the frontend API, which then calls the contract via _executeAndCheckSwaps().
Here is an example of the contract Here is an example of the contract of such a transaction Its whitelisted here
This way no fees are paid if a developer is using the LiFi contracts directly. Also it is using a mechanism that isn’t
suited for this. The _executeAndCheckSwaps() is geared for swaps and has several checks on balances. These
(and future) checks could interfere with the fee payments. Also this is a complicated and non transparent approach.
The project has suggested to see _executeAndCheckSwaps() as a multicall mechanism.
```

## Recommendation
Use a dedicated mechanism to pay for fees.
If _executeAndCheckSwaps() is intended to be a multicall mechanism then rename the function.
