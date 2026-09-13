# [H] tendermint-rs's Light Client Verifier allows malicious validators to spoof votes from other validators 

## Summary
Severity: High
Chain: tendermint-light-client-verifier
Component: tendermint-light-client-verifier
CWE: Incorrect Authorization
Published: 2025-04-09
Source: https://github.com/advisories/GHSA-6jrf-4jv4-r9mw
Type: github-advisory

## Details
Name: ISA-2025-003: Malicious validator can spoof votes from other validators 
Component: tendermint-rs
Criticality: High (Catastrophic Impact; Rare Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: <= v0.40.2
Affected users: Everyone

### Description

tendermint-rs contains a critical vulnerability in its light client implementation due to insecure handling of corrupted validator sets. Because it doesn't check that the validator address is correctly derived from the validator's public key when counting votes, it is possible to spoof votes from other validators. The result is being able to construct the malicious block and cheat the light client. The light client will accept such a block, seemingly signed by 2/3+ majority.

### Patches

The new tendermint-rs release [v0.40.3](https://github.com/informalsystems/tendermint-rs/releases/tag/v0.40.3) fixes this issue.

Unreleased code in the main branch is patched as well.

### Workarounds

There are no known workarounds for this issue.

### Timeline

* March 12, 2025, 13:41pm PST: Issue reported
* March 12, 2025, 03:00am PST: Core team completes validation of issue

This issue was reported by Felix Wilhelm from [Asymmetric Research](https://www.asymmetric.re/).
