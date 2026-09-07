# [M] Double-counting of `additionalCollateralFromUser` causes incorrect leverage decisions(DOS) in `DLoopIncreaseLeverageBase::increaseLeverage` function

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-21
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/192
Type: hats-finding

## Details
**Github username:** @OxTheAnzRider
  **Twitter username:** 0xtheanzrider
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/0xtheanzrider)

  **Beneficiary:** 0xF78554Dfb77e2Da05BAeE87913CA9706eD40a027
  **Submission hash (on-chain):** 0x68322bef8c855b1d904b2bb0a06f50af5544c7d2d15dfcfaa6ff952431c62ed0
  **Severity:** medium
  
  **Description:**
  In the function `increaseLeverage`, the amount of available collateral is computed as:
```solidity
uint256 collateralFromUser = additionalCollateralFromUser + collateralToken.balanceOf(address(this));
```
However, this leads to double-counting, since the user’s collateral (additionalCollateralFromUser) is already transferred into the vault and thus included in collateralToken.balanceOf(address(this))

This is an issue as the `DLoopIncreaseLeverageBase::increaseLeverage` function  uses  the `collateralFromUser` to perform a check to determuine whether to use a flash loan or not
```solidity

    function increaseLeverage(
        uint256 additionalCollateralFromUser,
        uint256 minOutputDebtTokenAmount,
        bytes calldata debtTokenToCollateralSwapData,
        DLoopCoreBase dLoopCore
    ) public nonReentrant returns (uint256 receivedDebtTokenAmount) {
        ERC20 collateralToken = dLoopCore.collateralToken();
        ERC20 debtToken = dLoopCore.debtToken();

        // Transfer any additional collateral token from user if provided
        if (additionalCollateralFromUser > 0) {
            collateralToken.safeTransferFrom(
                msg.sender,
                address(this),
                additionalCollateralFromUser
            );
        }

        // Calculate the required collateral amount to reach target leverage
        (uint256 requiredCollateralAmount, int8 direction) = dLoopCore
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/192_
