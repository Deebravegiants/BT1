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

After confirming the vulnerability, Cosmos Labs coordinated with the affected chain team and ecosystem partners to investigate the issue, deploy mitigations, and assist other chains running the affected code.

Cosmos Labs contacted chains known to be running versions containing the affected component to verify their configurations and support mitigation where necessary. At the time of publication, all known affected chains have either applied mitigations or upgraded to a patched version.

---

## Root Cause

The vulnerability was caused by incorrect state handling during nested EVM execution paths involving the ICS20 precompile.

Under certain execution conditions, state updates performed during recursive calls were not correctly reflected in the outer execution context. This could allow repeated use of the same token balance within a single transaction.

---

## Mitigation

As an immediate mitigation, chains were advised to disable the ICS20 precompile through a coordinated upgrade.

Cosmos Labs assisted ecosystem teams in verifying whether their chains were affected and in applying the mitigation where required.

- 15 chains were identified as running code containing the issue
- 6 chains did not have the affected feature enabled
- The remaining chains implemented the mitigation before exploitation occurred
- 1 chain experienced an exploit prior to mitigation

---

## Long-Term Fix

A permanent fix was implemented to ensure state consistency across nested EVM execution paths. The patch was distributed privately to affected teams for validation and later released publicly.

The fix is included in **[v0.6.0](https://github.com/cosmos/evm/releases/tag/v0.6.0)**.

---

## Am I Affected?

Chains may be affected if they:

- Run versions of the Cosmos EVM stack that include the ICS20 precompile implementation
- Have the ICS20 precompile enabled
- Have not upgraded to **v0.6.0** or applied the mitigation

Chains that have upgraded to **v0.6.0** or have disabled the ICS20 precompile are **not vulnerable to this issue**.

If you are unsure whether your chain is affected, please contact:

**[security@cosmoslabs.io](mailto:security@cosmoslabs.io)**

---

## Timeline

**July 2024**

The code containing the vulnerability was introduced upstream.

**January 21, 2026**

A network running the affected implementation experienced an exploit. The incident resulted in an estimated loss of approximately **$7M** on that network.

**January 21, 2026**

Cosmos Labs was notified of the potential vulnerability and began investigating.

**January 21–22, 2026**

The issue was reproduced and an initial mitigation was identified.

**Late January 2026**

Root cause analysis was conducted and a long-term fix was developed.

**Early February 2026**

The fix was validated internally and shared privately with affected ecosystem teams for review and testing.

**Mid February 2026**

Patches and mitigation guidance were distributed to chains running affected code.

**March 2026**

The permanent fix was released publicly as part of **v0.6.0**.

---

## Acknowledgements

We would like to thank the teams and security partners who collaborated with us during the investigation and remediation process, including contributors from:

- Saga
- B-Harvest
- Mantra
- Zellic
- Sherlock

Their collaboration and responsiveness helped accelerate investigation, validation of the fix, and coordinated mitigation across affected chains.

---

## Strengthening Security Processes

Following this incident, Cosmos Labs is implementing several improvements to further strengthen the security of the Cosmos EVM stack, including:

- Expanded fuzz testing focused on complex execution paths
- Additional auditing of state management logic across EVM integrations
- Improvements to testing frameworks for precompile functionality
- Continued collaboration with ecosystem security partners
- Increased our bug bounty payouts for our [security program](https://hackerone.com/cosmos)

These improvements are designed to reduce the likelihood of similar issues and ensure that teams building on the Cosmos stack can continue to rely on secure and well-tested infrastructure.

---

## Disclosure and Coordination

Cosmos Labs coordinated with ecosystem partners and affected teams to investigate the issue, validate mitigations, and distribute the permanent fix prior to public disclosure.

We appreciate the collaboration of ecosystem teams who assisted with investigation, validation, and responsible remediation of this issue.

---

## Responsible Disclosure

Cosmos Labs encourages responsible disclosure of potential vulnerabilities.

Security researchers who discover a potential issue are encouraged to report it privately so it can be investigated and addressed responsibly.

Reports can be submitted to:

**[security@cosmoslabs.io](mailto:security@cosmoslabs.io)**

Information about Cosmos Labs security programs and responsible disclosure practices, including bug bounty opportunities, will be made available through Cosmos Labs security channels, which can be signed up for [here](https://docs.google.com/forms/d/1Ae6ruTAw9zRoeN0xFxNbTfS-xCFdO68NGRsyFAeWHMc/edit).
