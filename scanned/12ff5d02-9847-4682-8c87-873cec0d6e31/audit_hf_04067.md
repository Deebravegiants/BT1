# [C] GLOBAL-1 | DoS Callbacks Through Simple Transfer

## Summary
Severity: Critical
Contest weight: 0.7640
Dataset id: 20520
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the callback afterWithdrawalExecution is triggered, it is checked that the amount of GM tokens sent to GMX to be redeemed match the amount of GM actually redeemed:
```solidity
Require.that(withdrawalInfo.inputAmount == _withdrawal.numbers.marketTokenAmount)
```
GMX records how much GM needs to be withdrawn by comparing the balance of GM before and after the function createWithdrawal is called. An attacker can easily cause a mismatch between withdrawalInfo.inputAmount and marketTokenAmount by sending 1 wei of GM to the Withdrawal Vault before an unwrapping is initiated.

The short or long token will be stuck in the Unwrapper Trader, the vault will remain frozen prohibiting any user execution, and the Core protocol will still believe the user holds the GM collateral which no longer truly exists. This will affect any user’s normal withdrawal as well as liquidations.

This attack is applicable to the afterDepositCancellation callback as well due to the following validation:
```solidity
assert(_deposit.numbers.initialLongTokenAmount == 0 || _deposit.numbers.initialShortTokenAmount == 0);
```
An attacker can send 1 wei to the Deposit Vault prior to the call of the createDeposit function, causing a revert at this assertion.

## Recommendation
Do not use a strict equality. Modify the validations such that the amounts of the event data are expected to be greater than or equal to the amounts Dolomite expects from its system. Furthermore, if two tokens are received from GMX upon cancellation, either deposit the unintended token into Dolomite if supported or send it to the Vault owner.
