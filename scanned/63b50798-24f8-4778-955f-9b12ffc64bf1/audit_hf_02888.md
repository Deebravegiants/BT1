# [H] GLOBAL-2 | Centralization Risk

## Summary
Severity: High
Contest weight: 0.1433
Dataset id: 16188
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Throughout the contracts there is a risk of admins and oracles using their privilege to beneﬁt
themselves or act malicious toward user’s holdings. Contracts utilizing the CustomAdmin access
control model face more risk as the number of admins or oracles increase because it only takes one
to act mischievous.
Additionally, the treasury which is under the in-house MultiSig.sol contract can be can be
manipulated by the principal admin who can unethically force a quorum.

## Recommendation
Ensure that privileged addresses such as admins are all a multi-sig and/or introduce a timelock for
improved community oversight. Secure a KYC for increased community trust.
