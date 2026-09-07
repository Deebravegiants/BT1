# [M] Collateral parameters can be overwritten

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-12-yetifinance
Published: 2021-12-22
Source: https://github.com/code-423n4/2021-12-yetifinance-findings/issues/198
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

It's possible to repeatedly add the first collateral token in `validCollateral` through the `Whitelist.addCollateral` function.
The `validCollateral[0] != _collateral` check will return false and skip further checks.

#### POC
Owner calls `addCollateral(collateral=validCollateral[0])`:

```solidity
function addCollateral(
    address _collateral,
    uint256 _minRatio,
    address _oracle,
    uint256 _decimals,
    address _priceCurve, 
    bool _isWrapped
) external onlyOwner {
    checkContract(_collateral);
    checkContract(_oracle);
    checkContract(_priceCurve);
    // If collateral list is not 0, and if the 0th index is not equal to this collateral,
    // then if index is 0 that means it is not set yet.
    // @audit evaluates validCollateral[0] != validCollateral[0] which is obv. false => skips require check
    if (validCollateral.length != 0 && validCollateral[0] != _collateral) {
        require(collateralParams[_collateral].index == 0, "collateral already exists");
    }

    validCollateral.push(_collateral);
    // overwrites parameters
    collateralParams[_collateral] = CollateralParams(
        _minRatio,
        _oracle,
        _decimals,
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-12-yetifinance-findings/issues/198_
