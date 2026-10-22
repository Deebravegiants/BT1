# [M] OmoVault does not enforce supplyCap

## Summary
Severity: Medium
Contest weight: 0.5608
Dataset id: 11007
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function deposit(
uint256 assets,
address receiver
) public virtual override onlyWhitelisted returns (uint256 shares) {
address msgSender = msg.sender;
// Check for rounding error since we round down in previewDeposit.
require((shares = _convertToShares(assets, false)) != 0, "ZERO_SHARES");
// require(supplyCap >= totalAssets() + assets, "SUPPLY_CAP_EXCEEDED");
// Need to transfer before minting or ERC777s could reenter.
asset.safeTransferFrom(msgSender, address(this), assets);
_totalAssets += assets;
_mint(receiver, shares);
emit Deposit(msgSender, receiver, assets, shares);
```

```solidity
function mint(
uint256 shares,
address receiver
) public virtual override onlyWhitelisted returns (uint256 assets) {
address msgSender = msg.sender;
assets = _convertToAssets(shares, true); // No need to check for rounding error, previewMint rounds up
// Need to transfer before minting or ERC777s could reenter.
asset.safeTransferFrom(msgSender, address(this), assets);
_totalAssets += assets;
_mint(receiver, shares);
emit Deposit(msgSender, receiver, assets, shares);
```

## Recommendation
Implement the supply cap check in both deposit() and mint() functions
