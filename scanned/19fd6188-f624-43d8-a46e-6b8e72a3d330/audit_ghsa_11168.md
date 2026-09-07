# [M] n8n Vulnerable to LDAP Filter Injection in LDAP Node

## Summary
Severity: Medium
Advisory: GHSA-w83q-mcmx-mh42
CVE: CVE-2026-33751
CWE: CWE-90
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-w83q-mcmx-mh42
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.27
- npm: `n8n` — affected >=2.14.0 <2.14.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.13.3

## Details
## Impact
A flaw in the LDAP node's filter escape logic allowed LDAP metacharacters to pass through unescaped when user-controlled input was interpolated into LDAP search filters. In workflows where external user input is passed via expressions into the LDAP node's search parameters, an attacker could manipulate the constructed filter to retrieve unintended LDAP records or bypass authentication checks implemented in the workflow.

Exploitation requires a specific workflow configuration:
- The LDAP node must be used with user-controlled input passed via expressions (e.g., from a form or webhook).

## Patches
The issue has been fixed in n8n versions 1.123.27, 2.13.3, and 2.14.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the LDAP node by adding `n8n-nodes-base.ldap` to the `NODES_EXCLUDE` environment variable.
- Avoid passing unvalidated external user input into LDAP node search parameters via expressions.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-w83q-mcmx-mh42
- https://nvd.nist.gov/vuln/detail/CVE-2026-33751
- https://github.com/n8n-io/n8n
