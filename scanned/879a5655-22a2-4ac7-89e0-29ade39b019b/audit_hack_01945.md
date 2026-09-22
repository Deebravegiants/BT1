# [M] 6.4 Pool Denial of Service

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

The first user to deposit into a newly created pool can immediately burn his pool tokens. In this case,
depositing into the pool no longer works, because the following check will revert:

```
if (poolTokenSupply == 0) {
if (stakedBalance > 0) {
revert InvalidStakedBalance();
}
}
```
A malicious user could create a bot that performs this attack cheaply by instantly depositing 1 wei base
tokens into any newly created pool.

Code corrected:

New deposits now reset the pool when pool token supply is 0 and staked balance is greater than 0.
