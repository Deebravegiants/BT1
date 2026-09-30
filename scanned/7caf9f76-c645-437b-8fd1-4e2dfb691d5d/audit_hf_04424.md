# [H] H-06 | Missing Blast Configurations

## Summary
Severity: High
Contest weight: 0.0325
Dataset id: 21900
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a missing initialization of the blast yield parameters in the LOOPSv1 module. During contract deployment the constructor does not set any values for the blast configuration, leaving the related storage slots at their default state (typically zero). Because later functions calculate rewards, interest or other financial outcomes based on these parameters, they operate on uninitialized data. As a result, the contract may distribute zero or otherwise incorrect yields, causing users to receive no expected payments while the protocol’s accounting assumes positive returns. This condition manifests as soon as the contract is live and any user attempts to claim or view blast‑related rewards; the UI may still display projected yields, but the actual transfer amount is zero or malformed. All participants who rely on blast yields – token holders, liquidity providers, or any role that expects periodic payouts – are affected. The issue was discovered during a manual audit where the reviewer inspected the constructor and noted the absence of any blast configuration code. It is subtle because the contract compiles and runs without reverting, so the problem only appears as a silent financial discrepancy rather than an explicit error. To remediate, the constructor should be amended to accept and store the correct blast yield values, with appropriate validation, ensuring that all downstream calculations use the intended parameters. Conceptually this is a classic case of missing or incomplete initialization of critical economic variables, leading to a reward‑distribution bug that violates the protocol’s business logic and expected accounting guarantees.

## Recommendation
Add blast yields configuration to the constructor.
