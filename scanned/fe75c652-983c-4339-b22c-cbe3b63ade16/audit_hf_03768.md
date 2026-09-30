# [M] Minting doesn't control for resulting zero shares

## Summary
Severity: Medium
Contest weight: 0.5947
Dataset id: 19941
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
It is possible to provide some amount of underlying to nwToken's mint and receive
zero shares, effectively losing the investment.
The situation of non-zero underlying investment and zero nwTokens to be minted is
a direct asset loss for a user and is not currently controlled.
Small amounts user provide can be lost fully. The damage looks to be mostly
reputational, although some downstream systems can malfunction on receiving
non-positive share amount.
Both ETH and ERC20 versions of mint() rounds the number of shares down, but do
not control for the resulting value to be positive:
te/contracts/external/adapters/nwToken.sol#L68-L80
// CEtherInterface functions
function mint() external payable nonReentrant override {
require(UNDERLYING_TOKEN == ETH_ADDRESS);
require(finalExchangeRate != 0);
if (msg.value == 0) return;
uint256 assetTokenAmount = _convertToAsset(msg.value);
// Handles event emission, balance update and total supply update
super._mint(msg.sender, assetTokenAmount);
_checkSupplyInvariant();
}
te/contracts/external/adapters/nwToken.sol#L82-L101
// CErc20Interface functions
function mint(uint mintAmount) external nonReentrant override returns (uint) {
require(UNDERLYING_TOKEN != ETH_ADDRESS);
require(finalExchangeRate != 0);
if (mintAmount == 0) return NO_ERROR;
ERC20(UNDERLYING_TOKEN).safeTransferFrom(
msg.sender,
address(this),
mintAmount
);
uint256 assetTokenAmount = _convertToAsset(mintAmount);
// Handles event emission, balance update and total supply update
super._mint(msg.sender, assetTokenAmount);
_checkSupplyInvariant();
return NO_ERROR;
}
```

## Recommendation
```solidity
Consider adding such control to prevent pure asset loss for a user:
te/contracts/external/adapters/nwToken.sol#L68-L80
// CEtherInterface functions
function mint() external payable nonReentrant override {
require(UNDERLYING_TOKEN == ETH_ADDRESS);
require(finalExchangeRate != 0);
if (msg.value == 0) return;
uint256 assetTokenAmount = _convertToAsset(msg.value);
require(assetTokenAmount != 0, "Zero shares");
// Handles event emission, balance update and total supply update
super._mint(msg.sender, assetTokenAmount);
_checkSupplyInvariant();
}
te/contracts/external/adapters/nwToken.sol#L82-L101
// CErc20Interface functions
function mint(uint mintAmount) external nonReentrant override returns (uint) {
require(UNDERLYING_TOKEN != ETH_ADDRESS);
require(finalExchangeRate != 0);
if (mintAmount == 0) return NO_ERROR;
ERC20(UNDERLYING_TOKEN).safeTransferFrom(
msg.sender,
address(this),
mintAmount
);
uint256 assetTokenAmount = _convertToAsset(mintAmount);
require(assetTokenAmount != 0, "Zero shares");
// Handles event emission, balance update and total supply update
super._mint(msg.sender, assetTokenAmount);
_checkSupplyInvariant();
return NO_ERROR;
}
```
