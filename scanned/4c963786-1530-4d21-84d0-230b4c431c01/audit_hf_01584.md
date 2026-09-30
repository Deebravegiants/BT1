# [H] MJR-1 Deposit will be unavailable if lending pool address will be

## Summary
Severity: High
Contest weight: 0.0331
Dataset id: 8496
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At line GenericAave.sol#L132 the deposit function assumes recent approval of token transfer. However, the safeApprove() is called once during contract initialization(GenericAave.sol#L49) and possible changes of lending pool address is not tracked properly. If lending pool address is updated by AAVE, the deposit() will be unavailable/reverted until contract replacement.

## Recommendation
Call safeApprove() on demand before calling deposit() on lending pool.
