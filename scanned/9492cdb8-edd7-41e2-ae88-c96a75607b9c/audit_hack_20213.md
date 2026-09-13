# [M] 5.3.1 Fee-On-Transfer tokens are not explicitly denied inswap().

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** SwapUtils.sol#L690-L729
**Description:** Theswap()function is used extensively within the Connext protocol, primarily when swapping be-
tween local and adopted assets. When a swap is performed, the function will check the actual amount transferred.
However, this is not consistent with other swap functions which check that the amount transferred is equal todx.
As a result, overwritingdxwithtokenFrom.balanceOf(address(this)).sub(beforeBalance)allows for fee-on-
transfer tokens to work as intended.
**Recommendation:** Consider adding arequire(dx == tokenFrom.balanceOf(address(this)).sub(beforeBalance),
"not support fee token");check prior to overwritingdxto ensure fee-on-transfer tokens are not used in the
swap.
**Connext:** Solved in PR 1642, in this commit.
**Spearbit:** Verified.
