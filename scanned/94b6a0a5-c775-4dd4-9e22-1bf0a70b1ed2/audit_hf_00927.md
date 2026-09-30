# [M] submitStrategy() DOS

## Summary
Severity: Medium
Contest weight: 0.0996
Dataset id: 2792
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Governance.submitStrategy() is strict to have only one pending strategy per vault. Moreover, no new strategy can be accepted for voting. It can only be accepted either after accepting or rejecting a pending strategy or after 6 hours after submission.
In addition, this function is public, so anyone can submit.
As a result, the simplest attack vector is spamming any new strategy as soon as submission is available. New submissions will have to wait 6 hours or governance step in. But after that the same spam attack is possible. It can also be frontrun transactions before submissions to block them.

## Recommendation
Consider allowing multiple pending strategies so that the attacker's submissions could be just ignored. Or allow submitting only for trusted addresses.
