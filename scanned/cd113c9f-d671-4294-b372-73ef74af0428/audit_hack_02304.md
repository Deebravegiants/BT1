# [H] \[H01\] Resolution upgrade inconsistency

## Summary
Severity: High
Source: https://github.com/OriginProtocol/origin-dollar/blob/bf4ff28d5944ecc277e66294fd2c702fee5cd58b/contracts/contracts/token/OUSDResolutionUpgrade.sol#L8
Type: audit-issue

## Details
The OUSD token achieves its rebasing functionality by tracking credit balances and scaling them by a conversion factor to retrieve the corresponding OUSD token balances. The `OUSDResolutionUpgrade` contract is designed as a temporary logic contract that replaces the token functionality with mechanisms to increase the precision of the conversion factors. In particular, there is [a function](https://github.com/OriginProtocol/origin-dollar/blob/bf4ff28d5944ecc277e66294fd2c702fee5cd58b/contracts/contracts/token/OUSDResolutionUpgrade.sol#L8) to update the global parameters and [a separate function](https://github.com/OriginProtocol/origin-dollar/blob/bf4ff28d5944ecc277e66294fd2c702fee5cd58b/contracts/contracts/token/OUSDResolutionUpgrade.sol#L17) to upgrade the individual user accounts in batches.

To avoid upgrading the same account multiple times, [an upgrade flag is set](https://github.com/OriginProtocol/origin-dollar/blob/bf4ff28d5944ecc277e66294fd2c702fee5cd58b/contracts/contracts/token/OUSDResolutionUpgrade.sol#L21) for each account. Similarly, [the upgrade flag is set](https://github.com/OriginProtocol/origin-dollar/blob/bf4ff28d5944ecc277e66294fd2c702fee5cd58b/contracts/contracts/token/OUSDResolutionUpgrade.sol#L10) for the zero address to indicate that the global parameters have been updated. There is no access control on either of these functions. This means that an attacker can include the zero address in a batch of account upgrades, which will set its flag and prevent anyone from upgrading the global state. This could produce an inconsistent state where a subset of the accounts use the new resolution, while the global parameters remain unchanged.

Consider restricting the `upgradeAccounts` function to non-zero account.

**Update:** _Fixed in [commit 95e8c90](https://github.com/OriginProtocol/origin-dollar/commit/95e8c90afbe9103d14e2dfba875acce08f108d3c)._
