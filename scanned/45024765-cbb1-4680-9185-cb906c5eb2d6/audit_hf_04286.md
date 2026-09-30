# [H] H-02 | Atomic Providers Cannot Be Configured

## Summary
Severity: High
Contest weight: 0.0934
Dataset id: 21425
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the setAtomicOracleProviderAfterSignal function the isOracleProviderEnabledKey is used instead of the isAtomicOracleProviderKey. As a result the atomicOracleProvider value cannot be set, preventing any price feed provider from atomic withdrawal use, and disallowing the atomic withdrawal feature.

## Recommendation
Change the isOracleProviderEnabledKey to the isAtomicOracleProviderKey.
