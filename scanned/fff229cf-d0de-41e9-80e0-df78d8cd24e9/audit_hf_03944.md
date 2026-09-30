# [M] OracleVersion latestVersionof Oracle.status()

## Summary
Severity: Medium
Contest weight: 0.1677
Dataset id: 20271
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This is because when Oracle.update(newProvider) is called, there is no requirement
that newProvider.latest().timestamp > oldProvider.latest().timestamp.
During the processLocal, encountering a non-existing version will result in using 0
as the makerValue, longValue, and shortValue to settle PNL, causing the user's
collateral to be deducted incorrectly.
This is because L350 is skipped (as the global has been settled to a newer
timestamp), and L356 enters the if branch.

## Proof of Concept
Given:
• At 13:40, The latest().timestamp of oracleProvider1 is 13:30
When:
• At 13:40, market.update(account1, ...)
– Store _versions[13:00] in L337
– Store _versions[13:30] in L353
latest().timestamp of oracleProvider2 is 13:20)
• market.update(account2) -> _settle(), L350 is skipped; L356 13:20 > 13:00,
enters _processPositionLocal():
– L436, nextPosition.timestamp == 13:20, version is empty;
– L440, context.local.accumulate with empty version will result in wrong
PNL.

## Recommendation
Consider requiring newProvider.latest().timestamp >
oldProvider.latest().timestamp in Oracle.update(newProvider).
