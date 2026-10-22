# [H] Missing zero-address validationfor burner address during initialization can break slashing

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23450
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The VaultTokenized contract's initialization procedure fails to validate that the burner parameter is a non-zero address. However, the onSlash function uses SafeERC20's safeTransfer to send tokens to this address, which will revert for most ERC20 implementations if the recipient is address(0).
```solidity
// In _initialize:
vs.burner = params.burner; // No validation that params.burner != address(0)
// In onSlash:
if (slashedAmount > 0) {
    IERC20(vs.collateral).safeTransfer(vs.burner, slashedAmount); // Will revert if vs.burner is
    address(0),!
}
```
While other critical parameters like collateral are validated against the zero address, the burner parameter lacks this check despite its importance in the slashing flow.

## Recommendation
Consider adding a zero-address validation for the burner parameter during initialization.
