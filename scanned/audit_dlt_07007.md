# [M] M-06 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/23
Type: code-finding

## Details
# Lines of code




# Vulnerability details

Mitigation of M-06: Issue NOT mitigated

## Mitigated issue
[M-06: Missing deadline check for AfEth actions](https://github.com/code-423n4/2023-09-asymmetry-findings/issues/43)

The issue was missing deadline checks for deposits and withdrawals.

## Mitigation review - missing deadline for rewards
Deadline parameters have been added to `AfEth.deposit()` and `AfEth.withdraw()`. Since access to VotiumStrategy has been restricted to AfEth these checks are only needed in AfEth.
However, the same issue applies to rewards deposits, where no deadline has been added. The entry points are `AfEth.depositRewards()` and `VotiumStrategyCore.applyRewards()`, where deadlines should also be added.
