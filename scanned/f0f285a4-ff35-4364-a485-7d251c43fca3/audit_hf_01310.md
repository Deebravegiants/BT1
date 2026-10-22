# [M] Incorrect asset calculation in maxWithdraw() function

## Summary
Severity: Medium
Contest weight: 0.5688
Dataset id: 6332
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are two issues with the maxWithdraw() implementation:
1. The withdraw() function calls super.maxWithdraw(owner) (which refers to ERC4626Upgradeable's implementation) instead of calling the overridden maxWithdraw() from WrappedDollarVault. This means the fee calculation in WrappedDollarVault's maxWithdraw() is bypassed.
2. The fee calculation in maxWithdraw() doesn't align with the fee calculation in previewWithdraw(), which leads to inconsistent behavior.

Impact Explanation:
The impact is medium. The incorrect calculation in maxWithdraw() can lead to a poor user experience where withdrawal transactions fail unexpectedly. It could also potentially lead to users being unable to withdraw their full entitled assets if the function underestimates the maximum amount. This creates confusion and may reduce trust in the protocol.

## Recommendation
1. Modify the withdraw() function to use the contract's own maxWithdraw() implementation, or simply make use of super.withdraw():
```solidity
function withdraw(
    uint256 assets,
    address receiver,
    address owner
)
    public
    override(ERC4626Upgradeable, IERC4626)
    whenNotPaused
    nonReentrant
    checkRouter
    returns (uint256)
{
    if (assets == 0) revert ZeroAmount();
    if (receiver == address(0)) revert NullAddress();
    return super.withdraw(assets, receiver, owner);
}
```
2. Reimplement maxWithdraw() to properly align with the fee calculation in previewWithdraw():
```solidity
function maxWithdraw(address owner)
    public
    view
    override(ERC4626Upgradeable, IERC4626)
    returns (uint256)
{
    if (paused()) return 0;
    // Get the maximum assets the user could withdraw without considering fees
    uint256 assets = super.maxWithdraw(owner);
    if (assets == 0) return 0;
    // Apply fee calculation consistent with previewWithdraw
    WrappedDollarVaultStorageV0 storage $ = _wrappedDollarVaultStorageV0();
    uint256 fee = _feeOnRaw(assets, $.feeRateBps);
    // Return the maximum assets after deducting fees
    return assets - fee;
}
```
