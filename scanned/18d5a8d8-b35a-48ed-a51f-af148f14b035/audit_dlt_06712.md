# [M] Missing (or Incorrect) post-execution check in `increaseLeverage()` open for over-leverage condition (exceeding `targetLeverageBps`)

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/63
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** chainnue
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/chainNue)

  **Beneficiary:** 0xABCDE0360aBCbA45098125E55437B005aE5DF46F
  **Submission hash (on-chain):** 0xccacbba5a1eb0adc09900af8723988fed74cbbbb39e8e87eec927bc32af2d100
  **Severity:** medium
  
  **Description:**
  **Description**\
The `increaseLeverage()` function predicts future leverage (`newLeverageBps`) based on current vault state and input values before performing supply and borrow actions. It then enforces a check to ensure the predicted leverage does not exceed `targetLeverageBps`. However, the function does not re-check the actual leverage after executing these actions. 

If we take a look at the `increaseLeverage()` there is this code:

```js
File: DLoopCoreBase.sol
1475:         // Calculate the new leverage after increasing the leverage
1476:         uint256 newLeverageBps = ((totalCollateralBase +
1477:             requiredCollateralTokenAmountInBase) *
1478:             BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) /
1479:             (totalCollateralBase +
1480:                 requiredCollateralTokenAmountInBase -
1481:                 totalDebtBase -
1482:                 borrowedDebtTokenInBase);
1483: 
1484:         // Make sure the new leverage is increasing and does not exceed the target leverage
1485:         if (
1486:             newLeverageBps > targetLeverageBps ||
1487:             newLeverageBps <= currentLeverageBps
1488:         ) {
1489:             revert IncreaseLeverageOutOfRange(
1490:                 newLeverageBps,
1491:                 targetLeverageBps,
1492:                 currentLeverageBps
1493:             );
1494:         }
1495.         ...
1496.         _supplyToPool(,..);
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/63_
