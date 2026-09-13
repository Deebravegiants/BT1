# [?] Prevent panic in TransactionByHash for non-existent transactions (#2373)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2025-01-14
Source: https://github.com/NethermindEth/juno/commit/0239e7780ab39c381ff95810ce1e370e0c5f4786
Type: security-commit

## Details
Prevent panic in TransactionByHash for non-existent transactions (#2373)

Fixes an issue where the code could panic when attempting to adapt a nil transaction in the pending block. This ensures the function gracefully handles non-existent transactions by returning ErrTxnHashNotFound.
