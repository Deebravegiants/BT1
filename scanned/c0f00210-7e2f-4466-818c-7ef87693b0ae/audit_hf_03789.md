# [M] getAccountPrimeDebtBalance() always return

## Summary
Severity: Medium
Contest weight: 0.5661
Dataset id: 19999
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Spelling errors that result in getAccountPrimeDebtBalance() Always return 0
getAccountPrimeDebtBalance() use for Show current debt
```solidity
function getAccountPrimeDebtBalance(uint16 currencyId, address account) external view override returns (
    int256 debtBalance
) {
    mapping(address => mapping(uint256 => BalanceStorage)) storage store = LibStorage.getBalanceStorage();
    BalanceStorage storage balanceStorage = store[account][currencyId];
    int256 cashBalance = balanceStorage.cashBalance;
    // Only return cash balances less than zero
    debtBalance = cashBalance < 0 ? debtBalance : 0;
    Always return 0
}
```
In the above code we can see that due to a spelling error, debtBalance always ==0
should use debtBalance = cashBalance < 0 ? cashBalance : 0;
getAccountPrimeDebtBalance() is the external method to check the debt If a third party integrates with notional protocol, this method will be used to determine whether the user has debt or not and handle it accordingly, which may lead to serious errors in the third party's business

## Recommendation
```solidity
function getAccountPrimeDebtBalance(uint16 currencyId, address account)
external view override returns (
    int256 debtBalance
) {
    mapping(address => mapping(uint256 => BalanceStorage)) storage store =
    LibStorage.getBalanceStorage();
    BalanceStorage storage balanceStorage = store[account][currencyId];
    int256 cashBalance = balanceStorage.cashBalance;
    // Only return cash balances less than zero
    debtBalance = cashBalance < 0 ? cashBalance : 0;
}
```
