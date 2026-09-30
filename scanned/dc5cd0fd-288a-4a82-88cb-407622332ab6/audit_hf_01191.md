# [M] Rogue Key Attacks Against BLS Aggregate Signature Veriﬁcation

## Summary
Severity: Medium
Contest weight: 0.0569
Dataset id: 5175
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The approach taken in this implementation is secure if either (1) the aggregated messages are unique, or (2) veriﬁcation keys are checked to have a proof of knowledge of the secret signing key. Otherwise, the scheme would be susceptible to "rogue key attacks".

## Recommendation
In addition to proofs of knowledge, there are a few other variants of BLS aggregate/multi signatures that protect against rogue key attacks. See the resources below for more information on options:
• BLS MultiSigs.
• BLS IRTF Docs.
