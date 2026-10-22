# [H] repayAccountPrimeDebtAtSettlement() user

## Summary
Severity: High
Contest weight: 0.7940
Dataset id: 20002
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
in repayAccountPrimeDebtAtSettlement() Incorrect calculation of primeCashRefund value (always == 0) Resulting in the loss of the user's residual cash
when settle Vault Account will execute
settleVaultAccount()->repayAccountPrimeDebtAtSettlement() In the repayAccountPrimeDebtAtSettlement() method the residual amount will be refunded to the user The code is as follows.
```solidity
function repayAccountPrimeDebtAtSettlement(
    PrimeRate memory pr,
    VaultStateStorage storage primeVaultState,
    uint16 currencyId,
    address vault,
    address account,
    int256 accountPrimeCash,
    int256 accountPrimeStorageValue
) internal returns (int256 finalPrimeDebtStorageValue, bool didTransfer) {
    ...
    if (netPrimeDebtRepaid < accountPrimeStorageValue) {
        // If the net debt change is greater than the debt held by the account, then only
        // decrease the total prime debt by what is held by the account. The residual amount
        // will be refunded to the account via a direct transfer.
        netPrimeDebtChange = accountPrimeStorageValue;
        finalPrimeDebtStorageValue = 0;
        int256 primeCashRefund = pr.convertFromUnderlying(
            pr.convertDebtStorageToUnderlying(netPrimeDebtChange.sub(accountPrimeStorageValue))
        );
        TokenHandler.withdrawPrimeCash(
            account, currencyId, primeCashRefund, pr, false // ETH will be transferred natively
        );
        didTransfer = true;
    } else {
```
From the above code we can see that there is a spelling error
1. netPrimeDebtChange = accountPrimeStorageValue;
2. primeCashRefund = netPrimeDebtChange.sub(accountPrimeStorageValue) so primeCashRefund always ==0
should be primeCashRefund = netPrimeDebtRepaid - accountPrimeStorageValue
primeCashRefund always == 0 , user lost residual cash

## Recommendation
```solidity
function repayAccountPrimeDebtAtSettlement(
    PrimeRate memory pr,
    VaultStateStorage storage primeVaultState,
    uint16 currencyId,
    address vault,
    address account,
    int256 accountPrimeCash,
    int256 accountPrimeStorageValue
) internal returns (int256 finalPrimeDebtStorageValue, bool didTransfer) {
    ...
    if (netPrimeDebtRepaid < accountPrimeStorageValue) {
        // If the net debt change is greater than the debt held by the account, then only
        // decrease the total prime debt by what is held by the account. The residual amount
        // will be refunded to the account via a direct transfer.
        netPrimeDebtChange = accountPrimeStorageValue;
        finalPrimeDebtStorageValue = 0;
        int256 primeCashRefund = pr.convertFromUnderlying(
            pr.convertDebtStorageToUnderlying(netPrimeDebtRepaid.sub(accountPrimeStorageValue))
        );
        TokenHandler.withdrawPrimeCash(
            account, currencyId, primeCashRefund, pr, false // ETH will be transferred natively
        );
        didTransfer = true;
    } else {
```
