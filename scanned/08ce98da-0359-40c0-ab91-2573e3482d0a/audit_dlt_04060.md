# [M] Deposit Cannot Be Used For Repayment When Rolling Position

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/80
Type: sherlock-finding

## Details
xiaoming90

high

# Deposit Cannot Be Used For Repayment When Rolling Position

## Summary

The user's deposit cannot be used for repayment when rolling a position.

## Vulnerability Detail

During rolling over a position, based on the comments below, it was understood that the vault allows a deposit from the user to be used as repayment for the lending. This is to allow an account to roll its position even if they are close to the max borrow capacity. However, it was observed that it is not possible for the users to do so.

https://github.com/sherlock-audit/2022-09-notional/blob/main/contracts-v2/contracts/external/actions/VaultAccountAction.sol#L135

```solidity
File: VaultAccountAction.sol
135:         // Takes a deposit from the user as repayment for the lending, allows an account to roll their position
136:         // even if they are close to the max borrow capacity.
137:         if (depositAmountExternal > 0) {
138:             vaultAccount.depositForRollPosition(vaultConfig, depositAmountExternal);
139:         }
```

Per the source code below, the deposit is credited into the user's vault account after the repayment. The repayment is executed at Line 122 via the `vaultAccount.lendToExitVault` function first, and then the user's deposit is credited into their account at Line 138 via the `depositForRollPosition` function.

https://github.com/sherlock-audit/2022-09-notional/blob/main/contracts-v2/contracts/external/actions/VaultAccountAction.sol#L87

```solidity
File: VaultAccountAction.sol
087:     function rollVaultPosition(
088:         address account,
089:         address vault,
090:         uint256 fCashToBorrow,
091:         uint256 maturity,
092:         uint256 depositAmountExternal,
093:         uint32 minLendRate,
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/80_
