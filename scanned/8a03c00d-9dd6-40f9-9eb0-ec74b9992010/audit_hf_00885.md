# [M] BoycoVault::totalAssets() uses asset.

## Summary
Severity: Medium
Contest weight: 0.4047
Dataset id: 2641
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
BoycoVault::totalAssets() calls super.totalAssets();, which is the ERC4626 function, that simply does return $._asset.balanceOf(address(this));. As such, it's possible to do donation the case. /// @dev Virtual accounting to avoid donations, asset valued denomination, returned in WAD BoycoVault:186 does not use virtual accounting. Internal Pre-conditions None. External Pre-conditions None. Attack Path Simple donation attack due to not using virtual accounting, that is, attacker mints 1 share and before a user deposits assets, the attacker donates assets and inflates the share price, making the vulnerable user loss all or part of its deposit due to rounding down. Loss of funds.

## Proof of Concept
ERC4626Upgradeable
```solidity
function totalAssets() public view virtual returns (uint256) {
    ERC4626Storage storage $ = _getERC4626Storage();
    return $._asset.balanceOf(address(this));
}
```

## Recommendation
Use virtual accounting.
