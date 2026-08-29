# [H] Withdraw reverts leading to DOS

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/73
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Tripathi)

  **Beneficiary:** 0x216a18e6F2E0199265a7A08B64A270f7fD967471
  **Submission hash (on-chain):** 0x1ec2d2e7511dafe92c12aaebd2a50307788eccc0501138e57870d3a05199a750
  **Severity:** high
  
  **Description:**
  Withdraw reverts leading to DOS

**Description**\
The `DStakeToken::withdraw()` redeem the vaultShares from the collateralVault and send the assets to the user. The current withdraw flow According to the docs is

*   **Withdraw:** User -> `DStakeToken.withdraw` -> `Router.withdraw` -> `CollateralVault.sendAsset` (to Router) -> `Adapter.convertFromVaultAsset` -> (Protocol Interaction) -> User receives dSTABLE -> `DStakeToken` burns shares.

Due to issue in the Protocol interaction part whole withdraw flow will revert and leads to DOS

**Attachments**

1. **Proof of Concept (PoC) File**


```solidity
File: contracts/vaults/dstake/DStakeToken.sol
    /**
     * @inheritdoc ERC4626Upgradeable
     * @dev Override to handle withdrawals with fees correctly.
     *      The `assets` parameter is the net amount of assets the user wants to receive.
     */
    function withdraw(
        uint256 assets,
        address receiver,
        address owner
    ) public virtual override returns (uint256 shares) {
        shares = previewWithdraw(assets); // Calculate shares needed for net amount
        uint256 grossAssets = convertToAssets(shares); // Calculate gross amount from shares

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/73_
