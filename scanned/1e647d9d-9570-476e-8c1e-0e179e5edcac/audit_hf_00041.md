# [M] EXNG-1 | Fixed Pool Can Lead to Bad Swaps

## Summary
Severity: Medium
Contest weight: 0.0739
Dataset id: 117
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Uniswap pools with the same token pair are differentiated by their configured fee tier. Currently, the poolFee is a constant, which means that swaps of that token pair can only occur in the specific pool that has that fee tier. If liquidity is low in this pool, swaps will occur with a larger price impact than they would otherwise in a different fee tier pool. This will lead to users and the protocol losing funds on swaps unnecessarily.

## Recommendation
Allow poolFee to be changed so that swaps can happen in the most advantageous pool.
