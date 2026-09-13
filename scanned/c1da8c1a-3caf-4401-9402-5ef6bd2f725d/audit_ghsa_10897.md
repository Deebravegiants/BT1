# [H] n8n: LDAP Email-Based Account Linking Allows Privilege Escalation and Account Takeover

## Summary
Severity: High
Advisory: GHSA-c545-x2rh-82fc
CVE: CVE-2026-33665
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-c545-x2rh-82fc
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.0.0-rc.0 <2.4.0
- npm: `n8n` — affected >=0 <1.121.0

## Details
## Impact
When LDAP authentication is enabled, n8n automatically linked an LDAP identity to an existing local account if the LDAP email attribute matched the local account's email. An authenticated LDAP user who could control their own LDAP email attribute could set it to match another user's email — including an administrator's — and upon login gain full access to that account. The account linkage persisted even if the LDAP email was later reverted, resulting in a permanent account takeover.

- LDAP authentication must be configured and active (non-default).

## Patches
The issue has been fixed in n8n versions 2.4.0 and 1.121.0. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable LDAP authentication until the instance can be upgraded.
- Restrict LDAP directory permissions so that users cannot modify their own email attributes.
- Audit existing LDAP-linked accounts for unexpected account associations.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-c545-x2rh-82fc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33665
- https://github.com/n8n-io/n8n
