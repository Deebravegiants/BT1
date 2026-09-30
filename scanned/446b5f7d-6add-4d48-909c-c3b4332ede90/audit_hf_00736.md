# [H] H-06 | Token Holder Vote Cannot Be Disputed

## Summary
Severity: High
Contest weight: 0.1735
Dataset id: 2292
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation dictates that once an escalation is decided by a token holders' vote, the
market either resolves to Finalized or reverts to OpenForResolution, with no mechanism to dispute
this decision.
However, according to the documentation, a third challenge window should exist, enabling any
holder of 250,000 TRUE tokens to dispute the escalation result and escalate the matter to the
Attesters.
The absence of this challenge window introduces a vulnerability where large TRUE token holders
could manipulate the vote for financial gain, leaving other stakeholders without any recourse to
contest the outcome.

## Recommendation
Introduce a third challenge window as outlined in the documentation, ensuring that escalation
decisions can be disputed and reviewed by the Attesters.
