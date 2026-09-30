# [H] H-01 | Second Challenge Period Can Be Bypassed

## Summary
Severity: High
Contest weight: 0.1551
Dataset id: 2311
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the market is in the MarketStatus.ResetByCouncil state, it should wait for the
secondChallengePeriod before opening for resolution to allow openEscalatedDispute. However,
proposeResolution can be called immediately without waiting for the secondChallengePeriod.
The bypass of secondChallengePeriod allows a dishonest disputor to move the market status to
ResolutionProposed therefore earning the resolver's bond before the resolver has a chance to
escalate the issue.

## Proof of Concept
https://github.com/GuardianAudits/truth-markets-1/pull/1/files

## Recommendation
Consider moving _updateStatus execution before setting councilDecisionAt = 0.
