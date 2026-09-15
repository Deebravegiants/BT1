# [M] 6.1 Incorrect Balance Check for Vault

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

Checking whether the MultiplyProxyActions contract holds enough funds has been modified to:

```
require(
cdpData.requiredDebt.add(cdpData.depositDai) >= IERC20(DAI).balanceOf(address(this)),
"requested and received amounts mismatch"
);
```
The check should ensure that the MultiplyProxyActions contract holds enough Dai for the operation on
the vault. Thus, if less DAI than needed is available the code should revert while a surplus of DAI could
be tolerated. However, the change proceeds with the execution if the balance is lower than the amount
needed while it reverts if there is a surplus of DAI.

Code corrected:

The condition has been changed to <=.
