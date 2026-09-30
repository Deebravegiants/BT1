# [M] M-11 | Risk Of Re-org Attack

## Summary
Severity: Medium
Contest weight: 0.0767
Dataset id: 2304
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the case of a block re-org event, disputors may unknowingly have submitted disputes for what
they believe to be the correct result, leading to slashing and the loss of their disputor bonds.
For example, consider the following scenario:
(1) Alice proposes an incorrect resolution.
(2) Bob disputes Alice’s resolution.
(3) A block re-org occurs and Alice’s proposal is replaced with a correct resolution.
(4) Bob’s dispute is invalid and will be punished.

## Recommendation
Allow disputors to pass the exact position they’d like to dispute to function openDispute.
