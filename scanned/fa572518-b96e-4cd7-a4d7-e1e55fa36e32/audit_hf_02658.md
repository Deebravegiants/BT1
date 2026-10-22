# [H] Default Values & Out-of-Bounds Panics In Merkle Tree Implementation

## Summary
Severity: High
Contest weight: 0.1966
Dataset id: 14399
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Merkle Tree implementation encounters an out-of-bounds error when processing sets with a large number of
elements exceeding 131,072.
Additionally, the utilization of default hashes to fill odd-sized trees allows for the default values to then be used to
successfully pass verification.
From tss/common/merkle_tree.go line [72]:
if rowSizeIsOdd {
leftSibling = elements[rowSize-1]
bz, _ := hexutil.Decode(defaults[depth]) // @audit, this should be assigned 0x00 instead of a default value, otherwise default
values will pass as valid. Also it will panic with out-of-bounds error for large arrays as `len(defaults) == 16`.
copy(buf[0:32], leftSibling[:])
copy(buf[32:64], bz)
elements[halfRowSize] = crypto.Keccak256Hash(buf)

## Recommendation
Instead of assigning default values to padded leafs, assign 0x00 value.
This would also eliminate out-of-bounds panics, which root cause is an insufficient number of default values to use.
