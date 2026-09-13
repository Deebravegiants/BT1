# [M] 5.1 Staking Does Not Prevent Misbehavior

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

Resolvers have to join a whitelist which is governed by the staking of 1inch tokens.

The documentation states:

```
The stake determines a resolver’s ability to get orders and ensures that a resolver
follow the protocol rules (like in proof of stake model).
```
On the smart contract level the implementation of the staking does not allow to seize stake of bad actors.
Their stake is not at risk and can simply be withdrawn at the end of the lock period hence this staking
does not ensure that a resolver follows the protocol rules.

Risk accepted:

1inch states:

```
They'll need only follow what is required to be able to settle the order batch.
Staking is only used as a threshold entry requirement.
```
