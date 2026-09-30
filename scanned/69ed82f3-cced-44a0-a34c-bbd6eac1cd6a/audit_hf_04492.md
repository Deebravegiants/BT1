# [M] M-01 | Lack Of Policy Permissions

## Summary
Severity: Medium
Contest weight: 0.0373
Dataset id: 22055
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BPOOL module contains a function called migrateBToken that is intended to be called only by authorized policy contracts. The contract enforces this restriction by checking that the caller’s policy has been granted permission for the function selector during the requestPermissions process. In the current deployment, no policy contract has been granted this specific selector, meaning that even legitimate policy calls are rejected. This misconfiguration originates from an incomplete access‑control setup: the developer added the function but omitted its selector from the list of allowed actions for any policy. When a migration is attempted—typically during an upgrade or token swap—the call reaches the permission check, fails, and the transaction reverts. As a result, the protocol cannot perform the intended token migration, effectively locking users’ BTokens and preventing the upgrade path from completing. From a user’s perspective, attempts to migrate their tokens appear to succeed on the UI but result in no change to their balances; the expected receipt of migrated tokens never arrives, leading to confusion and potential loss of confidence. The issue was discovered during a manual audit that inspected the policy permission matrix and identified that migrateBToken’s selector was absent. Because the function is not exercised in standard unit tests, the problem can remain hidden until a real migration is triggered, making it hard to notice during development. The vulnerability belongs to the class of “missing access‑control configuration” bugs, where a protected function is effectively unusable due to absent permissions. To remediate, the appropriate policy contract should be identified (for example, the upgrade manager) and its requestPermissions call should be updated to include the migrateBToken selector, or the function’s visibility and access control should be revised to match the intended workflow. Ensuring that the permission matrix accurately reflects all privileged actions will restore the ability to migrate tokens and prevent the denial‑of‑service condition currently affecting token holders and protocol administrators.

## Recommendation
Consider which policy is expected to call this function and add the function’s selector to the requestPermissions process.
