# [M] Harden-Runner: Bypassing Logging of Outbound Connections Using sendto, sendmsg, and sendmmsg in Harden-Runner (Community Tier)

## Summary
Severity: Medium
Advisory: GHSA-cpmj-h4f6-r6pq
CVE: CVE-2026-25598
CWE: CWE-221, CWE-778, CWE-863
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-cpmj-h4f6-r6pq
Type: github-advisory

## Affected
- GitHub Actions: `step-security/harden-runner` — affected >=0 <2.14.2

## Details
## Summary 

A security vulnerability has been identified in the Harden-Runner GitHub Action (Community Tier) that allows outbound network connections to evade audit logging. Specifically, outbound traffic using the `sendto`, `sendmsg`, and `sendmmsg` socket system calls can bypass detection and logging when using `egress-policy: audit`. 

**Note:** This vulnerability only affects audit mode. When using `egress-policy: block`, these connections are properly blocked. It requires the attacker to already have code execution capabilities within the GitHub Actions workflow (e.g., through workflow injection or compromised dependencies)

## Affected Versions 

- Harden-Runner Community Tier: All versions prior to v2.14.2 
- Harden-Runner Enterprise Tier: **NOT AFFECTED** 

## Severity 

**Medium** - This vulnerability affects audit logging capabilities but requires the attacker to already have code execution within the workflow. 

## Impact 

When Harden-Runner is configured in audit mode (`egress-policy: audit`), attackers with the ability to execute arbitrary code in a workflow can: 
- Send outbound network traffic without generating audit logs 
- Bypass network monitoring for UDP-based communications 

**Important:** This vulnerability requires the attacker to already have code execution capabilities within the GitHub Actions workflow (e.g., through workflow injection or compromised dependencies). 

## Technical Details 

The vulnerability stems from incomplete monitoring coverage of certain socket-related system calls. Specifically, the following system calls can be used to send UDP traffic without triggering audit events: 

- `sendto()` 

- `sendmsg()` 

- `sendmmsg()` 

An attacker with code execution in a workflow can compile and execute native code that uses these system calls to establish covert communication channels. 

## Affected Users 

**This vulnerability ONLY affects users of the Harden-Runner Community Tier.** 

The Harden-Runner Enterprise Tier is **NOT vulnerable** to this bypass technique. 

## Remediation 

### For Community Tier Users 
 
**Upgrade to Harden-Runner v2.14.2 or later.** This version includes fixes for the logging bypass vulnerability. 

### For Enterprise Tier Users 

No action required. Enterprise tier customers are not affected by this vulnerability. 

## Credit 

We would like to thank [Devansh Batham](https://github.com/devanshbatham) for responsibly disclosing this vulnerability through our security reporting process. Devansh was communicative throughout the process and verified the fix before the fix before it was made public.

## References
- https://github.com/step-security/harden-runner/security/advisories/GHSA-cpmj-h4f6-r6pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-25598
- https://github.com/step-security/harden-runner/commit/5ef0c079ce82195b2a36a210272d6b661572d83e
- https://github.com/step-security/harden-runner
- https://github.com/step-security/harden-runner/releases/tag/v2.14.2
