# [H] Lack of access control modifier on `mint()` function in the RollerPeriphery.sol

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-sense
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-sense-judging/issues/5
Type: sherlock-finding

## Details
0xmuxyz

high

# Lack of access control modifier on `mint()` function in the RollerPeriphery.sol

## Summary
- Lack of access control modifier on `mint()` function in the RollerPeriphery.sol

<br>

## Vulnerability Detail
- There is no access control modifier on the `mint()` function in the RollerPeriphery.sol
  https://github.com/sherlock-audit/2022-11-sense/blob/main/contracts/src/RollerPeriphery.sol#L59-L65


<br>

## Impact
- This vulnerability lead to that anyone (Any external users) can call `mint()` function in order to mint `any amount` of `vault shares` .


<br>

## Code Snippet
- There is no access control modifier on`mint()` function in the RollerPeriphery.sol
  https://github.com/sherlock-audit/2022-11-sense/blob/main/contracts/src/RollerPeriphery.sol#L59-L65
```solidity
    function mint(ERC4626 vault, uint256 shares, address receiver, uint256 maxAmountIn) external returns (uint256 assets) {
        ERC20(vault.asset()).safeTransferFrom(msg.sender, address(this), vault.previewMint(shares));

        if ((assets = vault.mint(shares, receiver)) > maxAmountIn) {
            revert MaxAssetError();
        }
    }
```

<br>

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sense-judging/issues/5_
