# [M] M-10 | donateLiquidity Should Update Market Borrowing

## Summary
Severity: Medium
Contest weight: 0.1111
Dataset id: 2110
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Whenever a pool's liquidity changes, the updateMarketBorrowing function must be called to snapshot cumulatedBorrowingPerUsd. This ensures the borrowing costs are accurately tracked and distributed across the pool participants. Currently, the donateLiquidity function does not perform this update. While this omission may not pose a risk when fees are donated through the fee distributor—since borrowing is updated during add/remove liquidity steps—donateLiquidity can also be called directly by external parties. This could lead to an inconsistency in cumulatedBorrowingPerUsd, particularly if significant liquidity is donated without triggering the borrowing update, impacting the fair distribution of borrowing costs.

## Recommendation
Ensure that updateMarketBorrowing is called within the donateLiquidity function
