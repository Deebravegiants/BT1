# [M] Incorrect fee calculation in withdraw and redeem functions

## Summary
Severity: Medium
Contest weight: 0.5929
Dataset id: 6331
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The calculations in previewRedeem() and previewWithdraw() use different mathematical approaches that result in inconsistent fee application:
1. In previewRedeem(), the contract:
   • Calculates fee shares directly: feeShares = _feeOnRaw(shares, feeRateBps).
   • Subtracts the fee from shares: netShares = shares - feeShares.
   • Returns assets corresponding to remaining shares: return super.previewRedeem(netShares).
2. In previewWithdraw(), the contract:
   • Calculates shares needed without fee: sharesWithoutFee = super.previewWithdraw(assets).
   • Calculates fee on those shares: feeShares = _feeOnRaw(sharesWithoutFee, feeRateBps).
   • Returns total shares needed: return sharesWithoutFee + feeShares.
The current implementation of previewWithdraw() uses the formula `shares = toShares(assets) * (1 + f)` However, the mathematically equivalent formula to previewRedeem() should be: `shares = toShares(assets / (1 - f))`

Impact Explanation:
The impact is medium. Users may receive more or fewer assets than expected when withdrawing from the vault. This discrepancy becomes more pronounced as the fee rate increases, potentially affecting users' financial positions and a loss in revenue.

## Recommendation
Replace the current fee calculation logic with a mathematically correct implementation.
1. Corrected fee calculation helper functions:
```solidity
function _feeOnRaw(
    uint256 amount,
    uint256 feeBasisPoints
)
    private
    pure
    returns (uint256)
{
    return amount.mulDiv(feeBasisPoints, BPS_DIVIDER, Math.Rounding.Ceil);
}

function _feeOnTotal(
    uint256 amount,
    uint256 feeBasisPoints
)
    private
    pure
    returns (uint256)
{
    return amount.mulDiv(
        feeBasisPoints, BPS_DIVIDER - feeBasisPoints, Math.Rounding.Ceil
    );
}
```
2. Corrected previewWithdraw() function:
```solidity
function previewWithdraw(uint256 assets)
    public
    view
    virtual
    override(ERC4626Upgradeable, IERC4626)
    returns (uint256)
{
    // Calculate fee amount
    WrappedDollarVaultStorageV0 storage $ = _wrappedDollarVaultStorageV0();
    uint256 fee = _feeOnTotal(assets, $.feeRateBps);
    // Calculate shares needed for assets + fee
    return super.previewWithdraw(assets + fee);
}
```
3. Corrected previewRedeem() function:
```solidity
function previewRedeem(uint256 shares)
    public
    view
    virtual
    override(ERC4626Upgradeable, IERC4626)
    returns (uint256)
{
    // Convert shares to assets
    uint256 assets = super.previewRedeem(shares);
    // Calculate and deduct fee
    WrappedDollarVaultStorageV0 storage $ = _wrappedDollarVaultStorageV0();
    uint256 fee = _feeOnRaw(assets, $.feeRateBps);
    return assets - fee;
}
```
4. Consolidate _withdrawAssets() and _redeemShares() into a single _withdraw() function:
```solidity
function _withdraw(
    address caller,
    address receiver,
    address owner,
    uint256 assets,
    uint256 shares
)
    internal
    virtual
    override
{
    WrappedDollarVaultStorageV0 storage $ = _wrappedDollarVaultStorageV0();
    address recipient = $.treasury;
    // Calculate fee shares
    uint256 feeShares = _feeOnRaw(shares, $.feeRateBps);
    // Call parent implementation to handle the withdrawal
    super._withdraw(caller, receiver, owner, assets, shares);
    // Mint fee shares to treasury
    if (feeShares > 0 && recipient != address(0)) {
        _mint(recipient, feeShares);
    }
}
```
By implementing these changes, the contract will correctly calculate fees and ensure users receive the expected amount of assets when withdrawing from the vault.
