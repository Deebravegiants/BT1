# [H] Method _deposit() in DLoopCoreBase can DoS due to incorrect debtAssetBorrowed calculation

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-24
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/233
Type: hats-finding

## Details
**Github username:** @cpp-phoenix
  **Twitter username:** 0xrochimaru
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/aarambh_audits)

  **Beneficiary:** 0x06a314624FBc79CEb00619a9703F9D2068890b2b
  **Submission hash (on-chain):** 0x43c2c064a29e90c555d47b6ccb75551fa79d7adf15b902971444cdedd4ed4bda
  **Severity:** high
  
  **Description:**
  **Description**\
In method `DLoopCoreBase::_deposit()`, `_borrowFromPool()` is called. This method has handing where `observedDiffBorrow` can be different from `amount` provided. In which case the difference till `BALANCE_DIFF_TOLERANCE` is accepted. So, `observedDiffBorrow` is the actual amount received by the contract, but the `_deposit()` method still tries to send `amount` to the `receiver`. So, if the received amount is less then the method will DoS at `debtToken.safeTransfer(receiver, debtAssetBorrowed);` call. Even though the tolerance was handled, still the method reverted because of insufficient balance. If more amount is received, then that amount will be left in the contract only. Leading to loss of funds that should've been sent to the user.

```solidity
        uint256 observedDiffBorrow = tokenBalanceAfterBorrow -
            tokenBalanceBeforeBorrow;
        if (observedDiffBorrow > amount) {
            if (observedDiffBorrow - amount > BALANCE_DIFF_TOLERANCE) {
                revert UnexpectedBorrowAmountFromPool(
                    token,
                    tokenBalanceBeforeBorrow,
                    tokenBalanceAfterBorrow,
                    amount
                );
            }
        } else {
            if (amount - observedDiffBorrow > BALANCE_DIFF_TOLERANCE) {
                revert UnexpectedBorrowAmountFromPool(
                    token,
                    tokenBalanceBeforeBorrow,
                    tokenBalanceAfterBorrow,
                    amount
                );
            }
        }
```

**Attack Scenario**\
Below highlighted lines showcase how the wrong borrowed amount returned will lead to either DoS or loss of funds.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/233_
