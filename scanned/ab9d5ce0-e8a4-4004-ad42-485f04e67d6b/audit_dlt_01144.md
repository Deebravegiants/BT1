# [?] core/vm, params: ensure order of forks, prevent overflow (#29023)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-02-19
Source: https://github.com/ethereum/go-ethereum/commit/ac0ff044606a663eeb47ef60ed5506f842753084
Type: security-commit

## Details
core/vm, params: ensure order of forks, prevent overflow (#29023)

This PR fixes an overflow which can could happen if inconsistent blockchain rules were configured. Additionally, it tries to prevent such inconsistencies from occurring by making sure that merge cannot be enabled unless previous fork(s) are also enabled.
