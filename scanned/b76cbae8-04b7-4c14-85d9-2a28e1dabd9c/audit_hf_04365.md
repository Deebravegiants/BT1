# [H] H-03 | Partial Vesting Claim Requests DoS’ed

## Summary
Severity: High
Contest weight: 0.1534
Dataset id: 21570
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Partial vesting claim requests occur when users claim before the vesting linear periods. When these claims are executed ORDER tokens are sent to the user in vault chain, but unclaimed amounts are transferred directly to the orderCollector in the ledger chain. The issue is that OmnichainLedgerV1 will never have ORDER token balance, so the safeTransfer will always fail as long as there is unclaimed amount. Therefore, users will need to wait for the full 90 days vesting period to be over as no partial claims are possible.

## Recommendation
Move the safeTransfer call to the LedgerOCCManager and create a function in OmnichainLedgerV1 so that unclaimed amounts can be transferred to the collector.
