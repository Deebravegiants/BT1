# [M] Withdraw too much can fail performance fee causing DoS

## Summary
Severity: Medium
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L239
Type: audit-issue

## Details
# Withdraw too much can fail performance fee causing DoS


## Summary

If before `initializeEpoch()`, user withdraw all the shares in the vault, the performance fee can not be transferred, and the initialization of new epoch will revert. Leaving the protocol inoperable. User and protocol fund could also be locked. The fee ought to be collected will be lost.


## Vulnerability Detail

Given:
1. During some epoch, the `netIncome` of the vault is $1,000
2. Before `initializeEpoch()`, user withdraw all of the shares in the vault, leaving less than $150 in the vault.
3. the call to `_collectPerformanceFee(l)` will fail, causing DoS, new epoch can not be initialized.


## Impact

- performance fee ought to be collected will be lost.
- protocol not able to function due to DoS, new epoch can not be initialized.
- user and protocol fund might be locked, due to DoS.

## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L239

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L174-L189


## Tool used

Manual Review


## Recommendation

Reserve a portion in vault, not allowed to be withdrawn, for the potential incoming performance fee.
