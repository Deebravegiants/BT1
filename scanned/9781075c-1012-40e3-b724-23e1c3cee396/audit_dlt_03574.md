# [M] Funds aren't distributed before changing distribution

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-reserve-mitigation
Published: 2023-08-22
Source: https://github.com/code-423n4/2023-08-reserve-mitigation-findings/issues/36
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/99d9db72e04db29f8e80e50a78b16a0b475d79f3/contracts/p1/Distributor.sol#L59-L63


# Vulnerability details

Mitigation does solve the issue, however there’s a wider issue here that funds aren’t distributed before set distribution is executed.
Fully mitigating the issue might not be possible, as it’d require to send from the backing manager to revenue trader and sell all assets for the `tokenToBuy`. But we can at least distribute the current balance before changing the distribution.



## Assessed type

Other
