# [M] Deleverage will revert incorrectly due to an underflow error

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-17
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/97
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0xf1440c95930f5c4232945c0f65d2390881c5f8cc16418a32c8a52335deb0dc69
  **Severity:** medium
  
  **Description:**
  **Description**\

Based on the current arrangement in the new leverage calculation when the system is overally levereged, and user tries to make necessary corrections the calculation operation substracts before adding causing the function to revert incorrectly.


  ```solidity
      // Calculate the new leverage after decreasing the leverage
        uint256 newLeverageBps = ((totalCollateralBase -
            withdrawCollateralTokenInBase) *
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) /

@audit>>            (totalCollateralBase -
                withdrawCollateralTokenInBase -
                totalDebtBase +
                requiredDebtTokenAmountInBase);    // error underflow revert. test  .

        // Make sure the new leverage is decreasing and is not below the target leverage

```

negative values don't exist, so subtracting a larger number from a smaller one causes a revert due to underflow in Solidity 0.8.x and above (where underflow/overflow checks are enforced by default).

Let's label it:


 ```solidity
denominator = totalCollateralBase - withdrawCollateralTokenInBase - totalDebtBase + requiredDebtTokenAmountInBase;

 ```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/97_
