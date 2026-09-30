# [M] M-1 Unjustiﬁed unlimited approvals

## Summary
Severity: Medium
Contest weight: 0.0528
Dataset id: 3659
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Several parts of code grant unlimited type(uint).max approvals even when it's not justiﬁable: • BebopSettlement.sol#L155 • BebopTransfer.sol#L103 No threat is inherent to it. However, it diminishes the overall contract security and could potentially be exploited by various attack vectors.

## Recommendation
It's recommended to grant approvals only for the exact amount that is anticipated to be spent.
