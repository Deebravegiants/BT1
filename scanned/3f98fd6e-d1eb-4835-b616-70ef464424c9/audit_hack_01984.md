# [M] 5.3 approve Only Allows the Values 0 and MAX

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

The approve function only allows the values 0 and type(uint256).max which could lead to the
following complications:

```
1.All approvals are infinite. In the past, infinite approvals given to buggy contracts have been
exploited (e.g., in the case of Multichain). The risk of this is increased when only infinite approvals
can be given.
2.All other approvals will fail. This breaks integration with existing DeFi protocols, which approve
exact values. Comet Tokens would be incompatible with such protocols.
```
Risk accepted:

Compound accepts the risk and refers to its documentation.
