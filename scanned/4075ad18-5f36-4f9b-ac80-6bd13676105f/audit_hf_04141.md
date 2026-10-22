# [H] ISU-2 | All Early Withdrawals Fail

## Summary
Severity: High
Contest weight: 0.1710
Dataset id: 20601
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The completeWithdrawalEarly function from the Issuance contract allows users to "buy out” the withdrawal of someone else in return for the withdrawal's equivalent in their desired LST/ETH. It checks the opposite of what it should. Only withdrawals that have a set root should continue being executed, when the check is doing quite the opposite. This will completely DoS the function from being used as intended and will further introduce unexpected behavior.

## Proof of Concept
https://github.com/GuardianAudits/RestPoCs/pull/6/files#diff-37c9f0775bfaf2121da179d90e12964f0992d8bb54fa6837d9943cb082dc1781

## Recommendation
if (pendingWithdraws.owner(root) == address(0)) revert UnknownRoot()
