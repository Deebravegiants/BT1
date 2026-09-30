# [M] M-06 | Invalid Outcome Voting In voteForDispute

## Summary
Severity: Medium
Contest weight: 0.0645
Dataset id: 2298
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Council members can cast votes referencing an invalid _winningPosition, one not recognized by the
market. If enough votes align on this invalid outcome, the dispute remains unresolvable.
Consequently, it remains open indefinitely, blocking certain system actions (e.g., adding or removing
council members) which require all disputes to be closed.

## Recommendation
Enforce strict _winningPosition validation in voteForDispute, reverting if _winningPosition falls
outside 1 to ITruthMarket(_market).positionCount().
