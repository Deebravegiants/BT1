# [H] CometBFT has inconsistencies between how commit signatures are verified and how block time is derived

## Summary
Severity: High
Advisory: GHSA-c32p-wcqj-j677
CWE: CWE-703
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-c32p-wcqj-j677
Type: github-advisory

## Affected
- Go: `github.com/cometbft/cometbft` — affected >=0.38.0-alpha.1 <0.38.21
- Go: `github.com/cometbft/cometbft` — affected >=0 <0.37.18

## Details
# CSA-2026-001: Tachyon

## Description

**Name:** CSA-2026-001: Tachyon

**Criticality:** Critical (Catastrophic Impact; Possible Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))

**Affected versions:** All versions of CometBFT

**Affected users:** Validators and protocols relying on block timestamps

## Description

A consensus-level vulnerability was discovered in CometBFT's "BFT Time" implementation due to an inconsistency between how commit signatures are verified and how block time is derived.

This breaks a core BFT Time guarantee: "A faulty process cannot arbitrarily increase the Time value."

## Impact

Downstream impact on chains affects any module, smart contract, or system that relies on the block timestamp.

## Patches

The new CometBFT releases [v0.38.21](https://github.com/cometbft/cometbft/releases/tag/v0.38.21) and [v0.37.18](https://github.com/cometbft/cometbft/releases/tag/v0.37.18) fix this issue. The `main` unreleased branch is also patched.

## Workarounds

There are no effective workarounds for this vulnerability. Upgrading to patched versions is required.

## Timeline

- January 8, 2026, 5:27PM UTC: Issue reported to Cosmos Bug Bounty Program
- January 9, 2026, 4:55AM UTC: Issue triaged and validated by core team
- January 12, 2026, 10:25PM UTC: Core team completes patch for the issue
- January 13, 2026 4:41PM UTC: Pre-notification delivered to ecosystem partners
- January 23, 2026, 3:00PM UTC: Patch made available

## Credits

This issue was reported to the Cosmos Bug Bounty Program on HackerOne. Credit to SEAL 911 and [QED Audit](https://x.com/QED_Audit) for the discovery and help with the patch.

If you believe you have found a bug in the Cosmos Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.

If you have questions about Cosmos security efforts, please reach out to our official communication channel at security@cosmoslabs.io.

A Github Security Advisory for this issue is available in the CometBFT repository. For more information about CometBFT, see https://docs.cometbft.com/.

## References
- https://github.com/cometbft/cometbft/security/advisories/GHSA-c32p-wcqj-j677
- https://github.com/cometbft/cometbft/commit/bf8274fcdbcab2bc652660ae627196a90a6efb97
- https://github.com/cometbft/cometbft
- https://github.com/cometbft/cometbft/releases/tag/v0.37.18
- https://github.com/cometbft/cometbft/releases/tag/v0.38.21
- https://pkg.go.dev/vuln/GO-2026-4361
