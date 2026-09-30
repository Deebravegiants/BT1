# [M] `setReserve`

## Summary
Severity: Medium
Contest weight: 0.1286
Dataset id: 1157
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `reserve` address variable in NestedFactory.sol remains equal to 0 before the `setReserve()` function is called by an owner. This may lead to incorrect transfers of tokens or invalid comparison with e.g., the asset reserve (nestedRecords.getAssetReserve(_nftId) == address(reserve)), should they occur before the value for `reserve` was set. In addition, the immutabiliy of the `reserve` variable requires extra caution when setting the value.

## Proof of Concept
`setReserve()`: [`NestedFactory.sol` L89](https://github.com/code-423n4/2021-11-nested/blob/5d113967cdf7c9ee29802e1ecb176c656386fe9b/contracts/NestedFactory.sol#L89)

## Recommendation
Consider initializing the value for the `reserve` variable in the constructor.

The main issue is duplicated : #60

The following comment can be considered as a duplicate of #83 if the extra caution is checking the zero address.

In addition, the immutabiliy of the reserve variable requires extra caution when setting the value.

The fact that the call to `setReserve` can be front-run is not being taken into account by the sponsor. I’m marking this one as not a duplicate.
