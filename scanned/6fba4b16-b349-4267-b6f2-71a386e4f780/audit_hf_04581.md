# [M] M-06 | Borrowers Pay For Paused Interest

## Summary
Severity: Medium
Contest weight: 0.1285
Dataset id: 22184
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
FraxlendPair has a function pause which pauses all actions in the pair and a function pauseInterest which pauses interest accrual. When interest is paused, new interest will not be accumulated and that's expected. However, once unpaused, the current borrowers will have to pay interest for the duration from the moment the protocol was paused until the current block. Since the protocol may function normally and have just its interest paused, that means new lenders and borrowers may come and go. This will cause a huge interest misaccounting. For example, interest is paused on Monday. Some borrowers leave the pair. and new ones enter it right before it's unpaused the next Monday. Since the lastUpdated timestamp will be the first monday, the new borrowers will immediately owe interest for that one week they were not even part of the pair.

## Recommendation
Update the timestamp when pauseInterest(false) is called currentRateInfo.lastTimestamp = uint64(block.timestamp);
