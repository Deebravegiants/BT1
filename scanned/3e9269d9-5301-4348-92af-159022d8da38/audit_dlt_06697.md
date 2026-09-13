# [M] Deposit will revert incorrectly because of a wrong calculation in the dloopdepositor Base

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-19
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/149
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0x08dac082505c12fca15b4e2efb048c21935fddc09ee6a82b88f381e2f35ba36b
  **Severity:** medium
  
  **Description:**
  **Description**\


When users deposit with a flashloan, the system uses the **target leverage** (like 3x) to guess how much debt token will be needed. But in reality, the vault uses the **current leverage** (like 2.85x or 3.15x) to decide how much to borrow.

This causes a problem.

If the current leverage is close to 3x but not exact (say 2.85x), the system borrows **less** debt token than expected. So, when it checks if enough debt was received to repay the flashloan (including fee), it wrongly thinks it wasn’t enough — and the deposit fails, even though it actually could repay.

---

### 🧨 **Why This Happens**

* Flashloan code assumes leverage is always **3x**.
* Actual borrow uses the **current leverage** (e.g., 2.85x).
* So it borrows **less**, which triggers this bad check:

  ```solidity
  if (debtReceived < debtSwappedIn + fee) revert();
  ```

Even though the vault has enough to pay back the loan, this check fails because it was expecting more.




  ```solidity

  function _deposit(
        address caller,
        address receiver,
        uint256 assets,
        uint256 shares
    ) internal override nonReentrant {
        /**
         * Example of how this function works:
         *
         * Suppose that the target leverage is 3x, and the baseLTVAsCollateral is 70%
         * - The collateral token is WETH
         * - The debt here is dUSD
         * - The current collateral token balance is 0 WETH
         * - The current debt token balance is 0 dUSD
         * - The current shares supply is 0
         * - Assume that the price of WETH is 2000 dUSD
         *
         * 1. User deposits 300 WETH
         * 2. The vault supplies 300 WETH to the lending pool
         * 3. The vault borrows 400,000 dUSD (300 * 2000 * 66.6666666%) from the lending pool
         *    - 66.666% is to keep the target leverage 3x
         * 4. The vault sends 400,000 dUSD to the receiver
         * 5. The vault mints 300 shares to the user (representing 300 WETH position in the lending pool)
         *
         * The current leverage is: (300 * 2000) / (300 * 2000 - 400,000) = 3x
         */

        // Make sure the current leverage is within the target range
        if (isTooImbalanced()) {
            revert TooImbalanced(
                getCurrentLeverageBps(),
                lowerBoundTargetLeverageBps,
                upperBoundTargetLeverageBps
            );
        }

        uint256 debtAssetBorrowed = _depositToPoolImplementation(
            caller,
            assets
        );

        // Transfer the debt asset to the receiver
        debtToken.safeTransfer(receiver, debtAssetBorrowed);

        // Mint the vault's shares to the depositor
        _mint(receiver, shares);

        emit Deposit(caller, receiver, assets, shares);
    }

  ```


Borrowed amount is calculated based on the current leverage 

  ```solidity
  /**
     * @dev Handles the logic of supplying collateral token and borrowing debt token
     * @param caller Address of the caller
     * @param supplyAssetAmount Amount of assets to supply
     * @return debtAssetAmountToBorrow Amount of debt asset to borrow
     */
    function _depositToPoolImplementation(
        address caller,
        uint256 supplyAssetAmount // supply amount
    ) private returns (uint256) {
        // Transfer the assets to the vault (need the allowance before calling this function)
        collateralToken.safeTransferFrom(
            caller,
            address(this),
            supplyAssetAmount
        );

        // At this step, we assume that the funds from the depositor are already in the vault

        // Get current leverage before supplying (IMPORTANT: this is the leverage before supplying)

@audit>>         uint256 currentLeverageBpsBeforeSupply = getCurrentLeverageBps();

        // Make sure we have enough balance to supply before supplying
        uint256 currentCollateralTokenBalance = collateralToken.balanceOf(
            address(this)
        );
        if (currentCollateralTokenBalance < supplyAssetAmount) {
            revert DepositInsufficientToSupply(
                currentCollateralTokenBalance,
                supplyAssetAmount
            );
        }

        // Supply the collateral token to the lending pool
        _supplyToPool(
            address(collateralToken),
            supplyAssetAmount,
            address(this)
        );

        // Get the amount of debt token to borrow that keeps the current leverage
        // If there is no deposit yet (leverage=0), we use the target leverage
        uint256 debtTokenAmountToBorrow = getBorrowAmountThatKeepCurrentLeverage(
                address(collateralToken),
                address(debtToken),
                supplyAssetAmount,

@audit>>                currentLeverageBpsBeforeSupply > 0
                    ? currentLeverageBpsBeforeSupply
                    : targetLeverageBps
            );

        // Borrow the max amount of debt token
        _borrowFromPool(
            address(debtToken),
            debtTokenAmountToBorrow,
            address(this)
        );

        return debtTokenAmountToBorrow;
    }
```


But when using flashloan, we calculate slippage and generate the amount of debt token needed, using the fixed TARGET leverage.


```solidity
 function deposit(
        uint256 assets, // deposit amount
        address receiver,
        uint256 minOutputShares,
        bytes calldata debtTokenToCollateralSwapData,
        DLoopCoreBase dLoopCore
    ) public nonReentrant returns (uint256 shares) {
        ERC20 collateralToken = dLoopCore.collateralToken();
        ERC20 debtToken = dLoopCore.debtToken();

        // Transfer the collateral token to the vault (need the allowance before calling this function)
        // The remaining amount of collateral token will be flash loaned from the flash lender
        // to reach the leveraged amount
        collateralToken.safeTransferFrom(msg.sender, address(this), assets);

        // Calculate the estimated overall slippage bps
 

@audit>>.        uint256 estimatedOverallSlippageBps = _calculateEstimatedOverallSlippageBps(
                dLoopCore.convertToShares(dLoopCore.getLeveragedAssets(assets)),
                minOutputShares
            );

        // Make sure the estimated overall slippage bps does not exceed 100%


@audit>>.        if (
            estimatedOverallSlippageBps >
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS
        ) {
            revert EstimatedOverallSlippageBpsCannotExceedOneHundredPercent(
                estimatedOverallSlippageBps
            );
        }

        // Calculate the leveraged collateral amount to deposit with slippage included
        // Explained with formula in _calculateEstimatedOverallSlippageBps()


@audit>>.        uint256 leveragedCollateralAmount = (dLoopCore.getLeveragedAssets(
            assets
        ) *
            (BasisPointConstants.ONE_HUNDRED_PERCENT_BPS -
                estimatedOverallSlippageBps)) /
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS;

        // Create the flash loan params data
        FlashLoanParams memory params = FlashLoanParams(
            receiver,
            assets,
            leveragedCollateralAmount,
            debtTokenToCollateralSwapData,
            dLoopCore
        );
        bytes memory data = _encodeParamsToData(params);
        uint256 maxFlashLoanAmount = flashLender.maxFlashLoan(
            address(debtToken)
        );

        // This value is used to check if the shares increased after the flash loan
        uint256 sharesBeforeDeposit = dLoopCore.balanceOf(address(this));



```


This will make

 The deposit to revert incorrectly.



```solidity
  /**
     * @dev Calculates the leveraged amount of the assets
     * @param assets Amount of assets
     * @return leveragedAssets Amount of leveraged assets
     */
    function getLeveragedAssets(uint256 assets) public view returns (uint256) {
        return
            (assets * targetLeverageBps) /
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS;
    }

```




```solidity

  // Make sure the debt token received after the deposit is not less than the debt token used in the swap
        // to allow repaying the flash loan
        if (
            debtTokenReceivedAfterDeposit <
            debtTokenAmountUsedInSwap + flashLoanFee
        ) {
            revert DebtTokenReceivedNotMetUsedAmountWithFlashLoanFee(
                debtTokenReceivedAfterDeposit,
                debtTokenAmountUsedInSwap,
                flashLoanFee
            );
        }
```



```solidity

    function getBorrowAmountThatKeepCurrentLeverage(
        address collateralAsset,
        address debtAsset,
        uint256 suppliedCollateralAmount,
        uint256 leverageBpsBeforeSupply
    ) public view returns (uint256 expectedBorrowAmount) {
        /* Formula definition:
         * - C1: totalCollateralBase before supply (in base currency)
         * - D1: totalDebtBase before supply (in base currency)
         * - C2: totalCollateralBase after supply (in base currency)
         * - D2: totalDebtBase after supply (in base currency)
         * - T: target leverage
         * - x: supply amount in base currency
         * - y: borrow amount in base currency
         *
         * We have:
         *      C1 / (C1-D1) = C2 / (C2-D2)
         *      C2 = C1+x
         *      D2 = D1+y
         *      C1 / (C1-D1) = T <=> C1 = (C1-D1) * T <=> C1 = C1*T - D1*T <=> C1*T - C1 = D1*T <=> C1 = D1*T/(T-1)
         *
         * Formula expression:
         *      C1 / (C1-D1) = (C1+x) / (C1+x-D1-y)
         *  <=> C1 * (C1+x-D1-y) = (C1+x) * (C1-D1)
         *  <=> C1^2 + C1*x - C1*D1 - C1*y = C1^2 - C1*D1 + C1*x - D1*x
         *  <=> C1*y = x*D1
         *  <=> y = x*D1 / C1
         *  <=> y = x * (T-1)/T
         *
         * Suppose that:
         *      T' = T * ONE_HUNDRED_PERCENT_BPS, then:
         *   => T = T' / ONE_HUNDRED_PERCENT_BPS
         * where:
         *      - T' is the target leverage in basis points unit
         *
         * This is the formula to calculate the borrow amount that keeps the current leverage:
         *      y = x * (T-1)/T
         *  <=> y = x * (T' / ONE_HUNDRED_PERCENT_BPS - 1) / (T' / ONE_HUNDRED_PERCENT_BPS)
         *  <=> y = x * (T' - ONE_HUNDRED_PERCENT_BPS) / T'
         */

        // Convert the actual supplied amount to base
        uint256 suppliedCollateralAmountInBase = convertFromTokenAmountToBaseCurrency(
                suppliedCollateralAmount,
                collateralAsset
            );

        // Calculate the borrow amount in base currency that keeps the current leverage
        uint256 borrowAmountInBase = (suppliedCollateralAmountInBase *
            (leverageBpsBeforeSupply -
                BasisPointConstants.ONE_HUNDRED_PERCENT_BPS)) /
            leverageBpsBeforeSupply;

        return convertFromBaseCurrencyToToken(borrowAmountInBase, debtAsset);
    }

```

Actual debt swapped is 132 e.g 


Required debt will be 


            200 * (2.85-1) /2.85 =129

Base has calculated 3x

            200 * (3-1) /3 = 133


when this values are compared, the received debt will be in adequate to repay back the flash loan and the call reverts.

But the check is actually capable of repaying back. 

1. 129 < 132 plus 1 fee will revert
2. Code was execting 133< 132 plus 1 fee. 




**Attack Scenario**\

The last check believes that the debt token plus fee will always be 3x of the collateral token which is not true has deposit use current leverage .

Vault’s current leverage = 2.85x (within range but < 3x target).

User deposits 100 WETH via flashloan.

Vault uses current leverage (2.85x) to compute debt borrow = 285 dUSD.

Flashloan path and slippage logic assume target leverage (3.00x) and compute swap for ≈ 290 dUSD.

Final balance after internal borrow: only 285 dUSD returned, but flashloan repayment expects 290 + fee.

The deposit reverts despite being correctly leveraged.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**

Get the current leverage as done in the deposit and calculate the actual amount to ensure the contract works without any incorrect reversion, based on the current state.
