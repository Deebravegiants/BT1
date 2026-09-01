# [M] Return value from `OdosSwapUtils.executeSwapOperation` mis-handled

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/17
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/tre)

  **Beneficiary:** 0x4C97Aa53fffF60dF05626aa1455418AF43F564e4
  **Submission hash (on-chain):** 0x9d5d4864b5271b17c9e632696308defe5b623a86897f0b7630b14cb984bb6792
  **Severity:** medium
  
  **Description:**
  **Description**

`OdosSwapLogic.swapExactOutput()` assumes the helper returns the amount of **output** received:

```solidity
uint256 actualAmountOut = OdosSwapUtils.executeSwapOperation(...);
if (actualAmountOut > amountOut) {           // treat as extra output
    uint256 surplus = actualAmountOut - amountOut;
    outputToken.safeTransfer(receiver, surplus);
}
return actualAmountOut;
```

But `executeSwapOperation()` actually returns the **input spent** (its own NatSpec and typical Odos usage).
Consequences:

* The `actualAmountOut > amountOut` branch will almost always be true, so the library tries to transfer
  `surplus` *output* tokens it never received, reverting the transaction and locking the flash-loan flow.
* Even if the transfer somehow succeeds (e.g. `outputToken` is also the vault’s input token), the numbers are nonsense.

**Attack Scenario**

Any route that consumes more than one unit of input (the normal case) triggers a revert, breaking `deposit`, `redeem`, `increaseLeverage`, and `decreaseLeverage` pathways that depend on this helper.
Funds can become stuck mid-flash-loan if the revert occurs after debt has been pulled.

**Recommendation**

* Rename the variable and align the logic:


_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/17_
