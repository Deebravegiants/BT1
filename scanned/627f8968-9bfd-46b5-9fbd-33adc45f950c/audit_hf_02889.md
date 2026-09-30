# [H] UB-1 | DoS Attack

## Summary
Severity: High
Contest weight: 0.0949
Dataset id: 16189
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious actor can call placeBet with different addresses, sending a tiny amount of ETH per call.
As a result, the YesBettors array and NoBettors array will expand to the point where it either exceeds
the block gas limit, or costs too much to reportResult. This will render the function inoperable.

## Recommendation
Use a pull-over-push withdrawal pattern such that the “for” loop can be avoided.
