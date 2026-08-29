# [C] Cosmos EVM: incorrect state handling during nested EVM execution paths

## Summary
Severity: Critical
Chain: github.com/cosmos/evm
Component: github.com/cosmos/evm
CWE: Always-Incorrect Control Flow Implementation
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-54gx-3cgr-7mfm
Type: github-advisory

## Details
**Advisory ID:** ASA-2026-002

**Component:** ICS20 Precompile

**Status:** Resolved

**Published:** March 2026

**Contact:** [security@cosmoslabs.io](mailto:security@cosmoslabs.io)

---

# Security Advisory ASA-2026-002

**Status: Resolved. A patch is available and all known affected chains have either applied mitigations or [upgraded](https://github.com/cosmos/evm/releases/tag/v0.6.0).**

| Field | Value |
| --- | --- |
| **Severity** | Critical |
| **Affected Component** | ICS20 Precompile |
| **Affected Versions** | Cosmos EVM implementations including the ICS20 precompile |
| **Patched Version** | [v0.6.0](https://github.com/cosmos/evm/releases/tag/v0.6.0) |
| **First Reported** | January 21, 2026 |
| **Public Disclosure** | March 2026 |

---

## Introduction

Recently, there was a vulnerability affecting a feature used by some chains built on the Cosmos EVM stack.  Working together with ecosystem partners and affected teams, particularly Saga, B-Harvest, Mantra, Zellic and Sherlock, Cosmos Labs  investigated the issue, coordinated mitigations, developed a permanent fix, and issued a patch to affected chains.

We appreciate the collaboration of the teams who assisted during the investigation and response process and thank our ecosystem partners for their support in coordinating mitigation and validation efforts.

---

## Remediation Summary

On January 21, 2026, Cosmos Labs was notified of suspicious activity on a network running the affected implementation. The issue resulted in financial loss on the Saga EVM network.

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-54gx-3cgr-7mfm_
