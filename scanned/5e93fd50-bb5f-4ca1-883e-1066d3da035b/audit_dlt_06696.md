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
            .getAmountToReachTargetLeverage(true); // Use vault token balance

        // Verify we need to increase leverage
        if (direction != 1) {
            revert("Current leverage is already at or above target");
        }

        //@audit it adds additionalCollateralFromUser to the collateralToken.balanceOf(address(this) tho the balance already accounts for it.
        // Calculate how much we need from flash loan
        uint256 collateralFromUser = additionalCollateralFromUser +
            collateralToken.balanceOf(address(this));

       //@audit uses the collateralFromUser to determine whether to use flash loan on not
        if (requiredCollateralAmount > collateralFromUser) {
            receivedDebtTokenAmount = _increaseLeverageWithFlashLoan(
                requiredCollateralAmount,
                collateralFromUser,
                additionalCollateralFromUser,
                debtTokenToCollateralSwapData,
                dLoopCore,
                collateralToken,
                debtToken
            );
        } else {
            // No flash loan needed, direct increase leverage
            uint256 leverageBeforeIncrease = dLoopCore.getCurrentLeverageBps();
            uint256 debtTokenBalanceBeforeIncrease = debtToken.balanceOf(
                address(this)
            );
```

Details: 
- additionalCollateralFromUser = 100

- collateralToken.balanceOf(address(this)) = 100 (user just transferred it)

- requiredCollateralAmount = 120
 then
```solidity
collateralFromUser = 100 (user input) + 100 (vault balance) = 200 (incorrect)
```
If
```solidity
if (requiredCollateralAmount > collateralFromUser) // 120 > 200 → false
```
The protocol skips flash loan logic, even though it only has 100, causing a DOS of the function as the contract doesn't have enough collateral token to increase the leverage.

**Impact**
- Incorrect logic path selection

- Inability to reach intended leverage ratio

- Flash loan logic skipped when needed

- economic los


**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**

Modify the code to use the contracts current balance instead of `additionalCollateralFromUser`  seeing as the `additionalCollateralFromUser` has already been sent to the contract:
```solidity
uint256 collateralFromUser = collateralToken.balanceOf(address(this));
```
