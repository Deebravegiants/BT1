# [M] RROU-2 | Inﬁnite Voting Power

## Summary
Severity: Medium
Contest weight: 0.0984
Dataset id: 19584
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When syncing an account's voting power, the user's staked amounts are compared against their current governance token wallet holdings. If the governance holdings are less, the appropriate amount is minted. This can be exploited if a user transfers their governance tokens to another account, triggers a sync, and then those governance tokens are minted again. This way, a user can generate inﬁnite votes and move forward malicious proposals.

## Proof of Concept
https://github.com/GuardianAudits/GMXV1Updates/blob/aa7755719e42389deae44528d6b2efbbbb84b4b7/test/guardian/Guardian.js#L358

## Recommendation
Ensure that the governance token used cannot be freely transferred.
