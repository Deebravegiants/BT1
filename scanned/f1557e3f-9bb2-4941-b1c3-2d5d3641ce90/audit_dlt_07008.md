# [M] H-02 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/13
Type: code-finding

## Details
# Lines of code




# Vulnerability details

Mitigation of H-02: Issue mitigated with ERROR

## Mitigated issue
[H-02: Zero amount withdrawals of SafEth or Votium will brick the withdraw process](https://github.com/code-423n4/2023-09-asymmetry-findings/issues/36)

The issue was that withdrawing afEth might imply a withdrawal of 0 safEth or vAfEth, which reverts.

## Mitigation review
In the case of withdrawing 0 safEth, [the call to SafEth.unstake() is now skipped in AfEth.withdraw()](https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/AfEth.sol#L284).
In the case of withdrawing 0 vAfEth, `AfEth.requestWithdraw()` still calls `VotiumStrategy.requestWithdraw(0)`. When finalizing the withdrawal with `AfEth.withdraw()`, which calls `VotiumStrategy.withdraw()`, [a check is made to only call `sellCvx()` with nonzero amounts](https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategy.sol#L143).
The request and withdrawal will thus not revert.

## Mitigation error
Since a `VotiumStrategy.requestWithdraw(0)` is still placed, this [queues it to the end of all previous withdrawal requests](https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategy.sol#L114) (as if an infinitesimal amount is to be withdrawn), incurring an artificially prolonged withdrawal time.
