# [M] MKTU-6 | Unequal Funding fees Over Equal Durations

## Summary
Severity: Medium
Contest weight: 0.1149
Dataset id: 19232
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Traders don't experience an incremental increase in the fundingFactorPerSecond. Instead, they receive funding based on the final funding factor applicable for the entire duration of their position. Consequently, a user who updates their position after X seconds will receive funding fees based on the rate at that specific moment. This could lead to a scenario where updating a position at the end of X seconds may yield more in funding fees than updating midway at X/2 and closing out another X/2 later, even though the total duration is the same.

## Proof of Concept
https://github.com/GuardianAudits/GMX-Updates-9-4-23/blob/25b1d86cbd3a807db6c7b03b3d0fe9d5b27ae924/test/guardian/PoCs.ts#L590

## Recommendation
Clearly document this behavior so that traders are aware how frequent updates can affect funding fee payments.
