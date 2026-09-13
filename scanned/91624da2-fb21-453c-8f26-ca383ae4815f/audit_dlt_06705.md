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

If this evaluates to a negative value, or a value that can't be represented as an unsigned integer (like 0 - 1), then it will revert.


E.g 1000 - 110 - 900 + 200 = will revert as solidity goes from left to right

1000 - 110 = 890 
890 - 900 =  - 10 will revert
so the caluculation will not even get to +200

Right calculation

1000 - 110 = 890
900 - 200 = 700

890 - 700 = 190.


**Attack Scenario**\
1. User calls to rebalance by deleveraging
2. Calculation incorrectly underflows

**Attachments**

1. **Proof of Concept (PoC) File**


```solidity
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("LeverageCalculator", function () {
  let leverage;

  before(async function () {
    const LeverageCalculator = await ethers.getContractFactory("LeverageCalculator");
    leverage = await LeverageCalculator.deploy();
    await leverage.deployed();
  });

  it("should revert due to underflow", async function () {
    const totalCollateralBase = 1000;
    const withdrawCollateralTokenInBase = 110;
    const totalDebtBase = 900;
    const requiredDebtTokenAmountInBase = 200;

    await expect(
      leverage.calculateNewLeverage(
        totalCollateralBase,
        withdrawCollateralTokenInBase,
        totalDebtBase,
        requiredDebtTokenAmountInBase
      )
    ).to.be.revertedWithPanic(); // Solidity 0.8+ underflow triggers Panic error
  });

  it("should return a valid leverage when values are safe", async function () {
    const result = await leverage.calculateNewLeverage(
      1000, // totalCollateralBase
      110,  // withdrawCollateralTokenInBase
      900,  // totalDebtBase
      200   // requiredDebtTokenAmountInBase
    );
    expect(result).to.be.a("bigint");
  });
});
```


2. **Revised Code File (Optional)**

The fix is to either compute additions first and then subtract or we handle this individual as debt and collateral and then subtract from each other.
