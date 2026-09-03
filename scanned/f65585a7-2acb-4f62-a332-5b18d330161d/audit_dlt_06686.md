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
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/306_
