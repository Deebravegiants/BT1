# [?] fix(node-rewards-canister): Fixes sync task not being rescheduled due to possible panic in closure (#9352)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-03-17
Source: https://github.com/dfinity/ic/commit/0831b63996d90143aa232448c02ae60fdafd5975
Type: security-commit

## Details
fix(node-rewards-canister): Fixes sync task not being rescheduled due to possible panic in closure (#9352)

This PR adds a recovery timer mechanism to ensure tasks are rescheduled
after a possible panic in the execution of the task.
This is done scheduling first a timer which reschedules the task itself
after sometime (15 min). If the task execution is successful the first
timer will be cancelled and the task rescheduled after chosen delay.
This fixes https://dfinity.atlassian.net/browse/SECFIND-2110

---------

Co-authored-by: IDX GitHub Automation <infra+github-automation@dfinity.org>
