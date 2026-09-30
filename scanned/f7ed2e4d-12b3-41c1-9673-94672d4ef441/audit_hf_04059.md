# [M] RH-3 | Wrong Gas Stipend Passed To Callback

## Summary
Severity: Medium
Contest weight: 0.1302
Dataset id: 20511
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The storage of AggregateVault has two variables for the two different gas fees that are paid by users when they create a request: executionGasAmount and executionGasAmountCallback. The former is for normal requests and the latter is for requests with callbacks.

The issue arises due to how executionGasAmountCallback is handled when calling the callback address the user provided. executionGasAmountCallback is passed directly as a gas stipend to the callback call even though it is intended to cover the whole call.

This issue causes the protocol, and more specifically the keeper, to provide a much higher gas stipend to the callback, resulting in loss of funds on every transaction. Another potential issue is the depletion of the keeper's ETH balance through large amounts of malicious requests aimed at disrupting deposits and withdrawals of innocent users.

## Recommendation
Consider passing executionGasAmountCallback - executionGasAmount as a gas stipend to callback calls.
