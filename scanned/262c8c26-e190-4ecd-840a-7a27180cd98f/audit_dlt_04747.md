# [M] Early user can manipulate _convertToAssets of vault, stealing funds from later depositers

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/94
Type: sherlock-finding

## Details
carrot

high

# Early user can manipulate _convertToAssets of vault, stealing funds from later depositers

## Summary
Early depositer can deposit and redeem 1 wei of asset. They can then manipulate the asset per share ratio and withdraw false number of assets from later depositers. This is a well-known attack vector of vault based contracts using precision loss.

## Vulnerability Detail
Malicious early user deposits 1 wei of assets into the queue, and then calls redeem function depositing that 1 wei into the vault and receive 1 wei of share token. Attacker can then send 1e18 -1 of asset token directly to the vault, making the price ratio of the vault equal 1e18 assets per share token. When future deposited deposits  19e17 tokens, that deposited only gets 1 wei of share token due to precision loss, instantly losing access to 9e17 asset tokens.

## Impact
Attacker profits from manipulating price and stealing funds from late depositors.

## Code Snippet

```solidity
function _deposit(
        address caller,
        address receiver,
        uint256 assetAmount,
        uint256 shareAmount,
        uint256 assetAmountOffset,
        uint256 shareAmountOffset
    ) internal virtual {
        uint256 assetAmountNet = assetAmount - assetAmountOffset;

        if (assetAmountNet > 0) {
            IERC20(_asset()).safeTransferFrom(
                caller,
                address(this),
                assetAmountNet
            );
        }

        uint256 shareAmountNet = shareAmount - shareAmountOffset;

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/94_
