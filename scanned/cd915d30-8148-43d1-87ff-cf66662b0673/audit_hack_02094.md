# [M] 6.4 Limitations of the TxPermissions Contract

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

The _allowedTxTypes function of the TxPermissions contract is applied to all transactions to be
include into a block. However this means all checks are only done on external transactions created from
externally owned accounts, internal transactions (calls within transactions) are not subject to these
checks.

Some of these checks including e.g.

```
if (validatorSetContract.isValidator(_to)) {
// Validator's mining address can't receive any coins
return (NONE, false);
}
```
can be circumvented by internal transaction. Internal transactions are calls from within bytecode
execution, e.g. during execution of a smart contract.

Risk Accepted:

POA Network is aware that the rules defined by the TxPermissions contracts are only applied to
transactions of EOAs.
