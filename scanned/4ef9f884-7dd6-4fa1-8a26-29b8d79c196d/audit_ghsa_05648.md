# [C] n8n Vulnerable to Unauthenticated File Access via Improper Webhook Request Handling

## Summary
Severity: Critical
Advisory: GHSA-v4pr-fm98-w9pg
CVE: CVE-2026-21858
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-v4pr-fm98-w9pg
Type: github-advisory

## Affected
- npm: `n8n` — affected >=1.65.0 <1.121.0

## Details
### Impact
A vulnerability in n8n allows an attacker to access files on the underlying server through execution of certain form-based workflows. A vulnerable workflow could grant access to an unauthenticated remote attacker. This could result in exposure of sensitive information stored on the system and may enable further compromise depending on deployment configuration and workflow usage.

### Patches
The issue has been fixed in n8n version 1.121.0. Users should upgrade to this version or later to remediate the vulnerability.

### Workarounds
No official workarounds are available. As a temporary mitigation, users may restrict or disable publicly accessible webhook and form endpoints until upgrading.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-v4pr-fm98-w9pg
- https://nvd.nist.gov/vuln/detail/CVE-2026-21858
- https://github.com/n8n-io/n8n
- https://www.cyera.com/research-labs/ni8mare-unauthenticated-remote-code-execution-in-n8n-cve-2026-21858
