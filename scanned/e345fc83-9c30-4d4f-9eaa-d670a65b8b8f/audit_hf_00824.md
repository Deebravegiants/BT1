# [H] H-03 | Liquidation Of Contract Accounts May Be Blocked

## Summary
Severity: High
Contest weight: 0.1301
Dataset id: 2560
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If an account is liquidatable on V2X, it is expected to be forcibly migrated to the V3 system where it will be liquidated. It cannot be liquidated on V2X. However, if the account is a contract that does not implement onERC721Received, then the V3 account cannot be transferred and the migration would fail. This allows contract accounts to avoid liquidation and create bad debt within the V2X system.

## Recommendation
Consider allowing the migration to proceed without an account transfer such that liquidation can continue, then provide some sort of claim mechanism for the account owner to recover remaining funds.
