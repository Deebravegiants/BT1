# [M] It is impossible to remove

## Summary
Severity: Medium
Contest weight: 0.1854
Dataset id: 20346
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
removeCollateral and removeInstrument implement the pop and swap method to remove entries from the array. It works for a majority of cases but fails if trying to remove the element at the end of the array, due to an OOB error.
uint256 collIdx = collateralIdx[collateral];
assert(collIdx < collAssets.length);
if (collAssets.length == 1) {
    collAssets.pop();
    collateralWhitelist[collateral] = false;
} else {
    collAssets[collIdx] = collAssets[collAssets.length - 1];
    collAssets.pop();
    collateralWhitelist[collateral] = false;
    collIdx is OOB after pop
}
When collateral is the last element of the array (collIdx == collAssets.length - 1) the swap doesn't actually swap any values. After the pop the length of the array will be shorter but collIdx == collAssets.length - 1 which will cause an OOB error for collAssets[collIdx].
Example: Collateral A is at the end of the collAssets array which has a length = 2. This means collIdx = 1. After collAssets.pop() length = 1 but collIdx = 1. Now collAssets[1] will result in an OOB error, because the max index is now 0.
removeInstrument and _revokeSigningKeyFromAccount also suffers from the same issue.
Last collateral/instrument is impossible to remove

## Recommendation
Extend the first if statement to include this edge case:
uint256 collIdx = collateralIdx[collateral];
assert(collIdx < collAssets.length);
if (collAssets.length - 1 == collIdx) {
    collAssets.pop();
    collateralWhitelist[collateral] = false;
} else {
    collAssets[collIdx] = collAssets[collAssets.length - 1];
    collAssets.pop();
    collateralWhitelist[collateral] = false;
    collateralIdx[collAssets[collIdx]] = collIdx;
}
