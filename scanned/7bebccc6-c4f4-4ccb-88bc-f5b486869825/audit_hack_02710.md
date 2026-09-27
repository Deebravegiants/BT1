# [M] `@solidstate/contracts/token/ERC4626/base/ERC4626Base.sol` are not implement ERC4626 properly.

## Summary
Severity: Medium
Reporter: exd0tpy
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultBase.sol#L4
Type: audit-issue

## Details
# `@solidstate/contracts/token/ERC4626/base/ERC4626Base.sol` are not implement ERC4626 properly.

## Summary
`@solidstate/contracts/token/ERC4626/base/ERC4626Base.sol` are not implement ERC4626 properly.
## Vulnerability Detail
ERC4626 must follow this rules.

* previewMint(uint256 shares) - Round Up ⬆
* previewWithdraw(uint256 assets) - Round Up ⬆
* previewRedeem(uint256 shares) - Round Down ⬇
* previewDeposit(uint256 assets) - Round Down ⬇
* convertToAssets(uint256 shares) - Round Down ⬇
* convertToShares(uint256 assets) - Round Down ⬇

But `@solidstate/contracts/token/ERC4626/base/ERC4626Base.sol` all function rounding down.

similar issue: https://github.com/code-423n4/2022-06-notional-coop-findings/issues/155
## Impact
This could be lead to user loss.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultBase.sol#L4

## Tool used
Manual Review

## Recommendation
Using OZ impelmentation.
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/14f98dbb581a5365ce3f0c50bd850e499c554f72/contracts/token/ERC20/extensions/ERC4626.sol
