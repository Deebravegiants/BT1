# [M] LockPositionService::increaseLockTime Inaccurate

## Summary
Severity: Medium
Contest weight: 0.1796
Dataset id: 20416
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LockPositionService::increaseLockTime uses block.timestamp for locking tokens, resulting in potential over-extension of the lock period. Specifically, if a user locks tokens near the end of a cycle, the lock duration might extend an additional week more than intended. For instance, locking for one cycle at the end of cycle N could result in an unlock time at the end of cycle N+2, instead of at the start of cycle N+2. This means that all the while specifying that their $CVG should be locked for the next cycle, the $CVG stays locked for two cycles.
The function increaseLockTime inaccurately calculates the lock duration by using block.timestamp, thus not aligned to the starts of cycles. This discrepancy leads to a longer-than-expected lock period, especially when a lock is initiated near the end of a cycle. This misalignment means that users are unintentionally extending their lock period and affecting their asset management strategies.
Scenario:
• Alice decides to lock her tokens for one cycle near the end of cycle N.
• The lock duration calculation extends the lock to the end of cycle N+2, rather than starting the unlock process at the start of cycle N+2.
• Alice's tokens are locked for an additional week beyond her expectation.

## Recommendation
Align the locking mechanism to multiples of a week and use (block.timestamp % WEEK) + lockDuration for the lock time calculation. This adjustment ensures that the lock duration is consistent with user expectations and cycle durations.
