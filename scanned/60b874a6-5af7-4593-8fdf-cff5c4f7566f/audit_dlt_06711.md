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

        require(
            grossAssets <= maxWithdraw(owner),
            "ERC4626: withdraw more than max"
        );

        _withdraw(_msgSender(), receiver, owner, grossAssets, shares); // Pass GROSS amount to _withdraw
        return shares;
    }


    /**
     * @inheritdoc ERC4626Upgradeable
     * @dev Calculates withdrawal fee, then delegates the core withdrawal logic
     *      (converting vault assets back to dSTABLE) to the router.
     *      The `assets` parameter is now the gross amount that needs to be withdrawn from the vault.
     */
    function _withdraw(
        address caller,
        address receiver,
        address owner,
        uint256 assets, // This is now the GROSS amount
        uint256 shares
    ) internal virtual override {

    ............................
        // Delegate conversion and vault update logic to router
        // Router is responsible for ensuring `amountToSend` of dSTABLE reaches the `receiver`.
        router.withdraw(amountToSend, receiver, owner);
    ............................
 
    }
```

1. user calls `withdraw()` with the net amount of assets needs to withdraw.
2. DStakeToken delegate the conversion and vault update logic to the router. 

```solidity
File: contracts/vaults/dstake/DStakeRouterDLend.sol

    function withdraw(
        uint256 dStableAmount,
        address receiver,
        address owner
    ) external override onlyRole(DSTAKE_TOKEN_ROLE) {
       ............................
        // 1. Determine vault asset and required amount
        address vaultAsset = adapter.vaultAsset();
        // Use previewConvertFromVaultAsset to get the required vaultAssetAmount for the target dStableAmount
        uint256 vaultAssetAmount = IERC4626(vaultAsset).previewWithdraw(
            dStableAmount
        );
        if (vaultAssetAmount == 0) revert ZeroPreviewWithdrawAmount(vaultAsset);

        // 2. Pull vaultAsset from collateral vault
        collateralVault.sendAsset(vaultAsset, vaultAssetAmount, address(this));

        // 3. Approve adapter (set required allowance using standard approve)
        IERC20(vaultAsset).approve(adapterAddress, vaultAssetAmount);

        // 4. Call adapter to convert and send dStable to receiver
        // Temporarily transfer to this contract, then forward to receiver if needed
        uint256 receivedDStable = adapter.convertFromVaultAsset(
            vaultAssetAmount
        );
       ............................
        // 5. Transfer ONLY the requested amount to the user
        IERC20(dStable).safeTransfer(receiver, dStableAmount);

        // 6. If adapter over-delivered, immediately convert the surplus dStable
        //    back into vault-asset shares so the value is reflected in
        //    totalAssets() for all shareholders.
        uint256 surplus = receivedDStable - dStableAmount;
        if (surplus > 0) {
            // Give the adapter allowance to pull the surplus
            IERC20(dStable).approve(adapterAddress, surplus);

            // Convert surplus dStable → vault asset (minted directly to the vault)
            (address mintedAsset, ) = adapter.convertToVaultAsset(surplus);
            ............................

            // Shares minted directly to collateralVault; surplus value now captured in accounting
            ............................
        }
       ............................

    }
```
3. Router will call `CollateralVault.sendAsset()` to send the vaultAsset to the router.
4. Now router calls `Adapter.convertFromVaultAsset()` to convert the vaultAsset to dStable.
5. It transfers the dStable to the user and tries to send the surplus dStable back to the collateralVault WHICH is the core issue here. sending surplus `dStable` back to the Aave aToken vault through `adapter.convertToVaultAsset()` can revert due to multiple reasons and DOS the withdraw.

If we see the `convertToVaultAsset()` function in the `WrappedDLendConversionAdapter.sol`, it will revert if `IERC4626(address(wrappedDLendToken)).deposit()` revert.

```solidity
    function convertToVaultAsset(
        uint256 dStableAmount
    )
    {
        ............................
        uint256 vaultAssetAmount = IERC4626(address(wrappedDLendToken)).deposit(
            dStableAmount,
            collateralVault
        );
        ............................
    }

```

Exploring various reason why `IERC4626(address(wrappedDLendToken)).deposit()` can revert

- AAVE Atoken vault have AAVE_ACTIVE_MASK, AAVE_FROZEN_MASK type AAVE_PAUSED_MASK state which is representation of whether the vault is active, frozen or paused. Aave blocks all [deposit](https://github.com/aave/Aave-Vault/blob/main/src/ATokenVault.sol#L581) in paused, frozen or inactive vaults while [withdraw](https://github.com/aave/Aave-Vault/blob/main/src/ATokenVault.sol#L610) is allowed in frozen state.
- if surplus is too small due to rounding error it could lead to 0 vault shares and aave doesn't allow such deposits. https://github.com/aave/Aave-Vault/blob/main/src/ATokenVault.sol#L529
