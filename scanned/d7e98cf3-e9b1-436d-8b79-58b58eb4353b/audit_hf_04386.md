# [M] M-14 | Lack Of Withdraw Functions

## Summary
Severity: Medium
Contest weight: 0.0704
Dataset id: 21602
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LedgerOCCManager, OCCManager (and potentially OmnichainLedgerV1) are expected to hold ORDER / USDC tokens which are burned or transferred when users claim.
The issue lies with the lack of a withdraw function for Owner to recover these tokens from the contract. Owner may wish to do this during a migration to a new contract.
Without a withdraw function, these tokens may become permanently stuck in the contract.

## Recommendation
Implement a withdraw function for the contracts which are expected to hold ERC-20 tokens.
