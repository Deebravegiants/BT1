# [H] n8n is Vulnerable to Credential Theft via Name-Based Resolution and Permission Checker Bypass in Community Edition

## Summary
Severity: High
Advisory: GHSA-m63j-689w-3j35
CVE: CVE-2026-33663
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-m63j-689w-3j35
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.27
- npm: `n8n` — affected >=2.14.0 <2.14.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.13.3

## Details
## Impact
An authenticated user with the `global:member` role could exploit chained authorization flaws in n8n's credential pipeline to steal plaintext secrets from generic HTTP credentials (`httpBasicAuth`, `httpHeaderAuth`, `httpQueryAuth`) belonging to other users on the same instance.

The attack abuses a name-based credential resolution path that does not enforce ownership or project scope, combined with a bypass in the credentials permission checker that causes generic HTTP credential types to be skipped during pre-execution validation. Together, these flaws allow a member-role user to resolve another user's credential ID and execute a workflow that decrypts and uses that credential without authorization.

Native integration credential types (e.g. `slackApi`, `openAiApi`, `postgres`) are not affected by this issue.

This vulnerability affects Community Edition only. Enterprise Edition has additional permission gates on workflow creation and execution that independently block this attack chain.

## Patches
The issue has been fixed in n8n versions 1.123.27, 2.13.3, and 2.14.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict instance access to fully trusted users only.
- Audit credentials stored on the instance and rotate any generic HTTP credentials (`httpBasicAuth`, `httpHeaderAuth`, `httpQueryAuth`) that may have been exposed.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-m63j-689w-3j35
- https://nvd.nist.gov/vuln/detail/CVE-2026-33663
- https://github.com/n8n-io/n8n
