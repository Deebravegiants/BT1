# [M] Performance fee setting does not confirm to business requirement in the documentation

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L150-L170
Type: audit-issue

## Details
# Performance fee setting does not confirm to business requirement in the documentation

## Summary

Performance fee setting does not confirm to business requirement in the documentation

## Vulnerability Detail

according to the documentation from the knox vault section:

> Performance Fee
A performance fee of 15% is charged on the net income of profitable vaults at the end of every epoch. Vaults that are not profitable in a given epoch do not incur a performance fee for that epoch.
To calculate the net income of a vault at the end of an epoch, the vault substracts the total assets at the end of the epoch from the total assets at the beginning of the auction adjusting for any withdrawals made between the end of the auction and the end of the epoch:
netIncome = totalAssets + totalWithdrawals - lastTotalAssets

Source: https://docs.knoxvaults.com/overview/fee-structure#performance-fee

however, the smart contract implementation of the performance fee setting does not confirm the requirement above in the function
setPerformanceFee

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L150-L170

then when we collect performance fee below, less fee are collected. 

function _collectPerformanceFee(VaultStorage.Layout storage l) in VaultInternal.sol

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L515-L522

## Impact

the project may failed to collect desired fee amount.

## Code Snippet

## Tool used

Manual Review

## Recommendation

https://docs.knoxvaults.com/overview/fee-structure#performance-fee

We recommand add lower limit and upper fee limit in the function setPerformanceFee to confirm the business requirement of the performance fee

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L155-L170
