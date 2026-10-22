# [M] 6.3 Miners Can Claim With Schedule Violation

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

The claim function calls the _getClaimable function to determine the amount users can claim
depending on the elapsed periods.

```
for (uint256 i = 0; i < schedule.durations.length; i++) {
uint128 scheduleDeadline = _addUint128(startTime, schedule.durations[i]);
// schedule deadline not passed, exiting
if (scheduleDeadline > _currentBlockTimestamp()) break;
// already claimed during this period, skipping
if (allocation.lastClaim > scheduleDeadline) continue;
claimable = _addUint128(claimable, _divUint128(_mulUint128(allocation.amount, schedule.percents[i]), MULTIPLIER));
}
```
At the end of claim execution, the allocation.lastClaim is reassigned, to disable repetitive claims
for the same period of the schedule.

```
allocation.lastClaim = _currentBlockTimestamp();
```
But if multiple claims will be send with block.timestamp equal to scheduleDeadline of some
schedule period, multiple repetitive claims of this blocks will be possible. This will effectively allow the
hackers to ignore the schedule. While this operation is hard to time right using regular transaction, miners
can craft such transactions.


Combined with nonexistent allocation.amount <= newClaimed check in claim function, this bug
also allows to claim more than the allocated amount.

Code corrected:

The condition in the loop was rewritten. Now the equality case will be skipped and repetitive claims for
the same periods of the schedule are not possible.

```
if (allocation.lastClaim >= scheduleDeadline) continue;
```
