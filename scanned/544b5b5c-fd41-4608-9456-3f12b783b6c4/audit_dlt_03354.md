# [H] function buyBond charges msg.sender twice

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-marginswap
Published: 2021-04-07
Source: https://github.com/code-423n4/2021-04-marginswap-findings/issues/38
Type: code-finding

## Details
# Email address

pauliax6@gmail.com


# Handle

paulius.eth


# Eth address

0x523B5b2Cc58A818667C22c862930B141f85d49DD


# Vulnerability details

function buyBond transfers amount from msg.sender twice:
  Fund(fund()).depositFor(msg.sender, issuer, amount);
  ...
  collectToken(issuer, msg.sender, amount);


# Impact

This makes the msg.sender pay twice for the same bond.


# Recommended mitigation steps

Charge poor man only once.
