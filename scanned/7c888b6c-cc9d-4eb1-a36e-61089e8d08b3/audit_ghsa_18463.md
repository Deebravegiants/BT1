# [H] Cosmos SDK's Integer Overflow vulnerability in its Validator Rewards pool can cause a chain halt

## Summary
Severity: High
Advisory: GHSA-p22h-3m2v-cmgh
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H/E:U (CVSS_V4)
Published: 2025-07-08
Source: https://github.com/advisories/GHSA-p22h-3m2v-cmgh
Type: github-advisory

## Affected
- Go: `github.com/cosmos/cosmos-sdk` — affected >=0 <0.50.14
- Go: `github.com/cosmos/cosmos-sdk` — affected >=0.52.0-alpha.1 <0.53.3

## Details
Description
Name: ISA-2025-005: Integer Overflow in Cosmos SDK
Component: CosmosSDK
Criticality: High (Considerable Impact; Likely Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: <= v0.50.13, <= 0.53.2
Affected users: Validators, Full nodes, Users on chains that utilize the distribution module
Cosmos SDK chains in unpatched releases that use the x/distribution module are affected.

Description
An issue was discovered in the distribution module where a malicious deposit into the Validator Rewards pool would result in an integer overflow that would cause a chain halt. A malicious validator can interact with the distribution module to introduce this state.

Patches
Has the problem been patched? What versions should users upgrade to?

The new Cosmos SDK release [v0.50.14](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.14) and [v0.53.3](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.53.3) fix this issue.

There are no known workarounds for this issue. It is advised that chains apply the update.

This issue was reported to the Cosmos Bug Bounty Program by `myte1111111` on HackerOne on April 15, 2025. If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.

If you have questions about Interchain security efforts, please reach out to our official communication channel at [security@interchain.io](mailto:security@interchain.io). For more information about the Interchain Foundation’s engagement with Amulet, and to sign up for security notification emails, please see https://github.com/interchainio/security.

## References
- https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-p22h-3m2v-cmgh
- https://github.com/cosmos/cosmos-sdk/commit/c4a14fa7b6828432fdabdb8b4af68ade9403ce49
- https://github.com/cosmos/cosmos-sdk/commit/f2e6295b662fdb27ea33da1296c29588ccdaab42
- https://github.com/cosmos/cosmos-sdk
