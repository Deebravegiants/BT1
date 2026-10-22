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
1497.         _borrowFromPool(...);
1498.         ...
```

which intended to make sure the `newLeverageBps` under the `targetLeverageBps`. But the issue here is, the `newLeverageBps` is being calculated based on the initial input, a pre-action forecast, so it's not the actual leverageBps after the tx (after the `_supplyToPool` and `_borrowFromPool` executed). 

If there is a minor discrepancies due to changes in internal calculation because of `_supplyToPool` and `_borrowFromPool` (because between forecast and after actual borrow/supply, dLEND updates internal indexes, interest accrues and liquidity index shifts) , there is a possible condition this will bypass the immutable `targetLeverageBps` value, and if so the positions will be over-leverage. This is surely a possible situation particularly relevant in high-utilization pools.

This became issue because over-leverage increases the chance of liquidation, especially in volatile markets, depositors can suffer partial or total loss. This should be fixed.

**Attack Scenario**\

1. Vault state before transaction:
   - Collateral: $200,000
   - Debt: $100,000
   - Leverage = 2.0x

2. User calls `increaseLeverage()`:
   - Supplies $100,000 in new collateral
   - Predicts borrow of $150,000
   - Forecast leverage (`newLeverageBps`) = 3.0x (check passes)

3. During transaction execution
   - Vault calls `_supplyToPool()` and `_borrowFromPool()`
   - These calls trigger interest accrual in dLEND
   - Existing debt grows from $100,000 to $100,500 (e.g, from accrued interest)
   - Total debt after borrow = 100,500 + 150,000 = $250,500

4. Post execution
   - Final collateral: $300,000
   - Final debt: $250,500
   - Actual leverage = 300,000 / (300,000 - 250,500) ≈ 3.03x

5. No post-check is enforced:
   - The vault ends up over-leveraged
   - Risk of liquidation and protocol-wide exposure

**Attachments**

2. **Revised Code File (Optional)**

Add a post-action safety check after all state-changing operations in `increaseLeverage()`:

```solidity
require(
    getCurrentLeverageBps() <= targetLeverageBps,
    "Final leverage exceeds target"
);
```

This ensures the vault state is compliant after execution and user is not in the status of an over-leverage situation which open for liquidation
