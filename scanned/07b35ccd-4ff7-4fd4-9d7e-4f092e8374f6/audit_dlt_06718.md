# [H] Division-by-Zero on First Withdraw in DLoopCoreBase

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/15
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/dod4ufn)

  **Beneficiary:** 0xf8e45a12a45CfBa70a24c00BC3492Ab948f028EE
  **Submission hash (on-chain):** 0x4ae0584bab4a35926daa35adb424d08fa36362e6aa382d0f202361d70738293f
  **Severity:** high
  
  **Description:**
  **Description**\
When a user removes collateral for the very first time (the vault has collateral but no debt),
_withdrawFromPoolImplementation() calls:

```solidity
uint256 leverageBpsBeforeRepayDebt = getCurrentLeverageBps();   // == 0
...
repaidDebtTokenAmount = getRepayAmountThatKeepCurrentLeverage(
        address(collateralToken),
        address(debtToken),
        collateralTokenToWithdraw,
        leverageBpsBeforeRepayDebt           // <-- passed as 0
);
```

getRepayAmountThatKeepCurrentLeverage() divides by that value:

```solidity
uint256 repayAmountInBase = (targetWithdrawAmountInBase *
        (leverageBpsBeforeRepayDebt - ONE_HUNDRED_PERCENT_BPS))
        / leverageBpsBeforeRepayDebt;        // ÷ 0 – revert
```
If the vault’s debt is still zero (leverage = 0 bps), any attempt to withdraw will invariably revert, permanently locking the very first depositor’s funds.

**Attack Scenario**\
A user supplies collateral to bootstrap the vault but never borrows.
Later they—or anyone rebalancing—try to withdraw: the call hits the division-by-zero check and reverts, freezing all liquidity.

**Recommendation**\

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/15_
