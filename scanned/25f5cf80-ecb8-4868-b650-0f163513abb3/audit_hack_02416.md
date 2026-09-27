# [M] Duplicate data

## Summary
Severity: Medium
Source: https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelToken.sol#L133
Type: audit-issue

## Details
The token contract `FuelToken` has a state variable [crowdfundEndsAt](https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelToken.sol#L133) which is hardcoded to be the same value as the `FuelCrowdfund`’s `endsAt` state variable. This duplication of the value is error-prone, as it could easily get out of sync. Consider getting the value directly from the crowdfund, as `crowdfund.endsAt()`.
