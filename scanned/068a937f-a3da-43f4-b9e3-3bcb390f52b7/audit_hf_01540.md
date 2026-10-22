# [H] Wrong transformation in function previewMintDebt(...)

## Summary
Severity: High
Contest weight: 0.7313
Dataset id: 8211
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the BorrowingVault.sol the function previewMintDebt(...) is supposed to take an amount of shares and turn them into an amount of debt. Currently it is taking the shares as if they were debt and turning them to shares.

```solidity
function previewMintDebt(uint256 shares) public view override returns (uint256 debt) {
    return _convertDebtToShares(shares, Math.Rounding.Down);
}
```

Recommendation
Change the function to use _convertToDebt(...) instead of _convertDebtToShares(...), as following

```solidity
function previewMintDebt(uint256 shares) public view override returns (uint256 debt) {
    return _convertToDebt(shares, Math.Rounding.Down);
}
```

## Recommendation
Recommendation not found
