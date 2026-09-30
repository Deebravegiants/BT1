# [M] 6.1 St1inch Can Be Locked Indefinitely

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

It is possible for an attacker to lock the staked amount of 1inch token of any staker by using one of the
St1inch.depositFor functions for the target address. By depositing a small amount of tokens and
specifying the duration, one can force a target staker to see its stake locked for more time, preventing the
staker to withdraw. The only way to break that attack would be to activate the emergency exit to allow the
target staker to withdraw.

Code corrected:

The functions St1inch.depositFor and St1inch.depositForWithPermit have been updated so
the duration cannot be specified and is hardcoded to be 0. This will only increase the deposited amount
and not the timelock duration.
