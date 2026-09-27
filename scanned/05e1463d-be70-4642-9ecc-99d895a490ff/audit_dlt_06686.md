# [M] Precision error in leverage calculation will result in early redeemers paying lesser debt than late redeemers and this will also cause deleveraging  to fail in maintaining the system (DOS to the deleverage call ).

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-07-01
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/306
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0x6854abe6e958642f807d71bc82f8c397e0937cadb859daf669e0c6f3c7668dd8
  **Severity:** medium
  
  **Description:**
  **Description**\

Due to the dynamic nature of leverage and the use of 10e4, which is 10,000, the basic point, debt distribution is incorrect, and the first redeemer will actually pay less debt to withdraw his max token.
A user who also calls to decrease leverage during this state will have his call DOSed/revert incorrectly.

```solidity

  /**
     * @dev Gets the current leverage in basis points
     * @return uint256 The current leverage in basis points
     */
    function getCurrentLeverageBps() public view returns (uint256) {
        (
            uint256 totalCollateralBase,
            uint256 totalDebtBase
        ) = getTotalCollateralAndDebtOfUserInBase(address(this));

        if (totalCollateralBase < totalDebtBase) {
            revert CollateralLessThanDebt(totalCollateralBase, totalDebtBase);
        }
        if (totalCollateralBase == 0) {
            return 0;
        }
        if (totalCollateralBase == totalDebtBase) {
            return type(uint256).max; // infinite leverage
        }
        // The leverage will be 1 if totalDebtBase is 0 (no more debt)
@audit>>        uint256 leverageBps = ((totalCollateralBase *
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) /
            (totalCollateralBase - totalDebtBase));
      



  if (leverageBps <= BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) {
            revert InvalidLeverage(leverageBps);
        }
        return leverageBps;
    }

```

E.g

Total collateral = 120e18
Total debt = 80e18 
Giving us a 30000 = 3x leverage


However, because of our integration with the Aave debt index and liquidity index, both the debt amount and the liquidity amount will increase with time. However, debt grows at a higher compound rate compared to liquidity provision.

For the sake of illustration

User A deposits 60
User B deposits 60

Each gets 40 debt tokens




Now the state reads after an increase in debt



120e18 and 80.001e18


New leverage = 120 * 10000 / 120 -80.001 =  30000.75002. = 30000 = 3x

User A withdraws and leaves with 60e18 and repays 40e18


But user B will be responsible for the increased debt due to the loss of precision.

If user B tries to leave the system, his call will revert because the calculated debt to cover will be less than the debt available in aave.

Aave will revert this because a system must always be overcollateralised.


Note this user cannot call deleverge before user A leaves because the system seems to be at 3x while in reality it is not 3x as the neglected values that were truncated will cause debt to be a lot more debt to cover. 


After user A leaves the contract the new leverage becomes


New leverage = 60 * 10000/ 60 - 40.001 = 30001.50008 = 30001 = 3.0001x


The leverage suddenly increased because of the debt left, which should have been shared between user A and B, and is now added as debt for user B alone.

```solidity

   // Calculate the repay amount in base
        uint256 repayAmountInBase = (targetWithdrawAmountInBase *
            (leverageBpsBeforeRepayDebt -
                BasisPointConstants.ONE_HUNDRED_PERCENT_BPS)) /
            leverageBpsBeforeRepayDebt;

```

USER calls to withdraw

Debt to repay = 60e18 * 30001 - 10000 / 30001 = 4.000066664* 10e19

But actually debt = 4.0001e18. 


This will revert on the Aave mainnet, as debt can never be > 0 and collateral = 0. The health check during withdraw from aave will revert this.




Even if we call deleverage after this, Part of user A collateral will be used to stabilise the debt owed by user A and B., meaning User B takes more debt impact than A.


```solidity


  function decreaseLeverage(
        uint256 additionalDebtTokenAmount,
        uint256 minReceivedAmount
    ) public nonReentrant {
        /**
         * Example of how this function works:
         *
         * Suppose that the target leverage is 3x, and the baseLTVAsCollateral is 70%
         * - The collateral token is WETH
         * - The debt here is dUSD
         * - Assume that the price of WETH is 2000 dUSD
         * - The current leverage is 4x
         *   - Total collateral: 100 WETH (100 * 2000 = 200,000 dUSD)
         *   - Total debt: 150,000 dUSD
         *   - Leverage: 200,000 / (200,000 - 150,000) = 4x
         *
         * 1. User call decreaseLeverage with 20,000 dUSD
         * 2. The vault transfers 20,000 dUSD from the user's wallet to the vault
         * 3. The vault repays 20,000 dUSD to the lending pool
         * 4. The vault withdraws 10 WETH (20,000 / 2000) from the lending pool
         * 5. The vault sends 10 WETH to the user
         *
         * The current leverage is now decreased:
         *    - Total collateral: 90 WETH (90 * 2000 = 180,000 dUSD)
         *    - Total debt: 130,000 dUSD
         *    - Leverage: 180,000 / (180,000 - 130,000) = 3.6x
         */
        // Make sure only decrease the leverage if it is above the target leverage

        (
            uint256 totalCollateralBase,
            uint256 totalDebtBase
        ) = getTotalCollateralAndDebtOfUserInBase(address(this));
        uint256 subsidyBps = getCurrentSubsidyBps();

        uint256 currentLeverageBps = getCurrentLeverageBps();
        if (currentLeverageBps <= targetLeverageBps) {
            revert LeverageBelowTarget(currentLeverageBps, targetLeverageBps);
        }

        // Need to calculate the required debt token amount before transferring the additional debt token
        // to the vault as it will change the current debt token balance in the vault
        uint256 requiredDebtTokenAmount = _getRequiredDebtTokenAmountToRebalance(
                targetLeverageBps,
                totalCollateralBase,
                totalDebtBase,
                subsidyBps,
                additionalDebtTokenAmount
            );

        // Only transfer the debt token if there is an additional amount to repay
        if (additionalDebtTokenAmount > 0) {
            // Transfer the additional debt token from the caller to the vault
            debtToken.safeTransferFrom(
                msg.sender,
                address(this),
                additionalDebtTokenAmount
            );
        }

        // Calculate the amount of debt token in base currency
        uint256 requiredDebtTokenAmountInBase = convertFromTokenAmountToBaseCurrency(
                requiredDebtTokenAmount,
                address(debtToken)
            );

        // The amount of collateral asset to withdraw is equal to the amount of debt token repaid
        // plus the subsidy (bonus for the caller)
        uint256 withdrawCollateralTokenInBase = (requiredDebtTokenAmountInBase *
            (BasisPointConstants.ONE_HUNDRED_PERCENT_BPS + subsidyBps)) /
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS;

        // Calculate the new leverage after decreasing the leverage
        uint256 newLeverageBps = ((totalCollateralBase -
            withdrawCollateralTokenInBase) *
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) /
            (totalCollateralBase +
                requiredDebtTokenAmountInBase -
                withdrawCollateralTokenInBase -
                totalDebtBase );    // error underflow revert. test  

        // Make sure the new leverage is decreasing and is not below the target leverage
        if (
            newLeverageBps < targetLeverageBps ||
            newLeverageBps >= currentLeverageBps
        ) {
            revert DecreaseLeverageOutOfRange(
                newLeverageBps,
                targetLeverageBps,
                currentLeverageBps
            );
        }

        // Repay the debt token to the lending pool
        _repayDebtToPool(
            address(debtToken),
            requiredDebtTokenAmount,
            address(this)
        );

        // Withdraw collateral
        uint256 withdrawnCollateralTokenAmount = convertFromBaseCurrencyToToken(
            withdrawCollateralTokenInBase,
            address(collateralToken)
        );

        // Slippage protection, to make sure the user receives at least minReceivedAmount
        if (withdrawnCollateralTokenAmount < minReceivedAmount) {
            revert RebalanceReceiveLessThanMinAmount(
                "decreaseLeverage",
                withdrawnCollateralTokenAmount,
                minReceivedAmount
            );
        }

        // At this step, the _withdrawFromPool wrapper function will also assert that
        // the withdrawn amount is exactly the amount requested, thus we can safely
        // have the slippage check before calling this function
        _withdrawFromPool(
            address(collateralToken),
            withdrawnCollateralTokenAmount,
            address(this)
        );

        // Transfer the collateral asset to the user
        collateralToken.safeTransfer(
            msg.sender,
            withdrawnCollateralTokenAmount
        );
    }

```

Also this will affect subsidyBps calculation has at 30001




```solidity

 subsidyBps =
                ((currentLeverageBps - targetLeverageBps) *
                    BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) /
                targetLeverageBps;
```


subsidyBps = (300001 - 30000) * 10000 / 30000 = 10000/30000 = 0


hence even if user calls deleverage the system will not deleverage has subsidy will be 0 hence no change will occur to the total debt and total asset ratio wise.



Impact

This creates a Denial of Service to user B and the deleverager.

1. User B cannot withdraw all assets
2. Decrease leverage will not work has no subsidy means debt added equal collateral added which will result in newleverage being equal to the current leverage which will revert.


```solidity
 // Make sure the new leverage is decreasing and is not below the target leverage
        if (
            newLeverageBps < targetLeverageBps ||
            newLeverageBps >= currentLeverageBps
        ) {
            revert DecreaseLeverageOutOfRange(
                newLeverageBps,
                targetLeverageBps,
                currentLeverageBps
            );
        }
```




**Attack Scenario**\

Precision errors will cause User B to accumulate more debt than User A, favouring the early user to exit and leaving more debt for users remaining in the contract.

The debt value can become enormous, favouring whales or large capital users who exit, leaving Users with less capital to manage their residual debt.

subsidyBps calculation will also cause deleveraging and increase leverage not to work after a slight deviation between debt and collateral.


**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**

Consider increasing the bps to 1e18; this will eliminate the precision error by a 10e18 factor while ensuring proper debt distribution among users. This will also ensure that subsidy Bps can handle as small as 30001 or less in leverage calculation changes.
