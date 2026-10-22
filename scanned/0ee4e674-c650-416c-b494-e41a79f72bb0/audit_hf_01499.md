# [H] H-6 maxInvocations should be limited

## Summary
Severity: High
Contest weight: 0.0857
Dataset id: 7951
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
TokenId contains collactionId, versionId and tokenNumber. maxInvocations is a parameter that
determines the max tokenNumber. Due to using versionId, tokenNumber should be < 10_000, otherwise the
versionId logic would be broken.
FantiumNFTV3.sol#L528
FantiumNFTV3.sol#L691

## Recommendation
We recommend adding the following check: maxInvocations < 10_000.
