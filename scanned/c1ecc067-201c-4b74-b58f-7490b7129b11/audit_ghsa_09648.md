# [M] n8n has SQL Injection in Oracle Database Node via Limit Field

## Summary
Severity: Medium
Advisory: GHSA-r6jc-mpqw-m755
CVE: CVE-2026-42233
CWE: CWE-20, CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-r6jc-mpqw-m755
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.32
- npm: `n8n` — affected >=2.18.0 <2.18.1
- npm: `n8n` — affected >=2.0.0 <2.17.4

## Details
## Impact
A flaw in the Oracle Database node's select operation allowed user-controlled input passed into the `Limit` field via expressions to be interpolated directly into the SQL query without sanitization or parameterization. In workflows where external input is passed into the `Limit` field (e.g., from a webhook), an attacker could inject arbitrary SQL and exfiltrate data from the connected Oracle database.

Exploitation requires a specific workflow configuration:
- The Oracle Database node must be used with user-controlled input passed via expressions into the `Limit` field.
- Authentication requirements depend on the workflow's configuration (e.g., an unauthenticated webhook endpoint would allow unauthenticated exploitation).

## Patches
The issue has been fixed in n8n versions 1.123.32, 2.17.4, and 2.18.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Oracle Database node by adding `n8n-nodes-base.oracleDatabase` to the `NODES_EXCLUDE` environment variable.
- Avoid passing unvalidated external user input into the Oracle Database node's `Limit` field via expressions.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-r6jc-mpqw-m755
- https://nvd.nist.gov/vuln/detail/CVE-2026-42233
- https://github.com/n8n-io/n8n
