# [C] CSA-2026-001: Tachyon 

## Summary
Severity: Critical
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-01-23
Source: https://github.com/cometbft/cometbft/security/advisories/GHSA-c32p-wcqj-j677
Type: github-advisory

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


_Trimmed to 38 lines — full report: https://github.com/cometbft/cometbft/security/advisories/GHSA-c32p-wcqj-j677_
