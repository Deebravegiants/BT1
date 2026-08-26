# [M] Vests can be denied

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-11-vader
Published: 2021-11-15
Source: https://github.com/code-423n4/2021-11-vader-findings/issues/169
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The `LinearVesting.vestFor` function (which is called by `Converter`) reverts if there already exists a vest for the user:

```solidity
 require(
    vest[user].amount == 0,
    "LinearVesting::selfVest: Already a vester"
);
```

There's an attack where a griefer frontruns the `vestFor` call and instead vests the smallest unit of VADER for the `user`.
The original transaction will then revert and the vest will be denied

## Recommended Mitigation Steps
There are several ways to mitigate this.
The most involved one would be to allow several separate vestings per user.
