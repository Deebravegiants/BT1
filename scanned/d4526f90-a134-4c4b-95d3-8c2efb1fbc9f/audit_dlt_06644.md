# [M] Price Calculation Discrepancy in Asset Conversion

## Summary
Severity: Medium
Chain: Smart contract
Component: Euro-Dollar
Published: 2024-11-04
Source: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/34
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** ACai_sec
**Submission hash (on-chain):** 0x33d536198fecda7c86619265c0e63f9b8400261c847e74836e4591b11fa232c7
**Severity:** medium

**Description:**
**Description**\
A vulnerability exists in the price calculation mechanism between deposits and withdrawals in the InvestToken contract. The issue arises due to inconsistent price references when converting between assets (USDE) and shares, potentially causing users to suffer losses during emergency withdrawals.

**Attack Scenario**\
```solidity
// In InvestToken.sol
function deposit(uint256 assets, address receiver) public returns (uint256 shares) {
    shares = convertToShares(assets);  // Uses currentPrice
    usde.burn(msg.sender, assets);
    _mint(receiver, shares);
}

function withdraw(uint256 assets, address receiver, address owner) public returns (uint256 shares) {
    shares = convertToShares(assets);  // Uses currentPrice for calculation
    _burn(owner, shares);
    usde.mint(receiver, assets);
}

// In YieldOracle.sol
function assetsToShares(uint256 assets) external view returns (uint256) {
    return Math.mulDiv(assets, 10 ** 18, currentPrice);
}

function sharesToAssets(uint256 shares) external view returns (uint256) {
    return Math.mulDiv(shares, previousPrice, 10 ** 18);  // Uses previousPrice
}
```
Consider the following scenario:

Initial state:
```solidity

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/34_
