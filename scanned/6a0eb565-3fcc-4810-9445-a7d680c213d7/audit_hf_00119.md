# [H] Proposals can be cancelled

## Summary
Severity: High
Contest weight: 0.1111
Dataset id: 279
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anyone can cancel any proposals by calling `DAO.cancelProposal(id, id)` with `oldProposalID == newProposalID`. This always passes the minority check as the proposal was approved.

An attacker can launch a denial of service attack on the DAO governance and prevent any proposals from being executed.

Recommend checking that `oldProposalID` == `newProposalID`

This is valid, can fix with a `require()`

## Recommendation
No recommendation
