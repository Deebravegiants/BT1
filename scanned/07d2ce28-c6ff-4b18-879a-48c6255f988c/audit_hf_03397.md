# [M] OCL-1 | Lack Of Sequencer Uptime Check

## Summary
Severity: Medium
Contest weight: 0.0592
Dataset id: 18505
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Even with the heartbeat validation, it may be prudent to validate that the Sequencer is active to
prevent stale pricing.
This would avoid any scenarios where price movement triggers an update within the heartbeat
duration but the new price is not reported to the L2, allowing traders to take advantage of stale
pricing.

## Recommendation
Validate whether the Sequencer is active or not. Furthermore, document keeper behavior in the case
that the Sequencer is down.
