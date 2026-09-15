# [M] Attacker might disable trading by faking a report violation

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-reserve-mitigation
Published: 2023-08-22
Source: https://github.com/code-423n4/2023-08-reserve-mitigation-findings/issues/40
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/99d9db72e04db29f8e80e50a78b16a0b475d79f3/contracts/plugins/trading/DutchTrade.sol#L212-L214


# Vulnerability details

Dutch trade now creates a report violation whenever the price is x1.5 then the best price.
The issue is that the attacker can fake a report violation by buying with the higher price. Since revenue traders don't have a minimum trade amount that can cost the attacker near zero funds.

Mitigation might be to create violation report only if the price is high and the total value of the sell is above some threshold.


## Assessed type

Other
