# [M] Unchecked return value

## Summary
Severity: Medium
Source: https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelToken.sol#L202
Type: audit-issue

## Details
The function [finalizeCrowdfund](https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelToken.sol#L202) is defined to return a boolean value indicating success. However, this return value is [ignored](https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelCrowdfund.sol#L84) when the function is called. Since the return value is currently always `true`, consider removing it altogether. Otherwise, always check the return value.

_**Update:** The return value was removed in [f85fc45](https://github.com/etherparty/FUEL-Contracts/commit/f85fc459519fb63803acdfc2de52744838b83338)._
