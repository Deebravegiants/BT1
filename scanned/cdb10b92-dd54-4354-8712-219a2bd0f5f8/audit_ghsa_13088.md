# [M] Sentry vulnerable to incorrect credential validation on OAuth token requests

## Summary
Severity: Medium
Advisory: GHSA-hgj4-h2x3-rfx4
CVE: CVE-2023-39531
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-hgj4-h2x3-rfx4
Type: github-advisory

## Affected
- PyPI: `sentry` — affected >=10.0.0 <23.7.2

## Details
### Impact

An attacker with sufficient client-side exploits could retrieve a valid access token for another user during the OAuth token exchange due to incorrect credential validation. The client ID must be known and the API application must have already been authorized on the targeted user account. 

### Remediation

- **Sentry SaaS** customers do not need to take any action. Those with the highest risk will be contacted directly by Sentry.
- **Self-hosted installations** should upgrade to version 23.7.2 or higher.

### Workarounds

There are no direct workarounds, but users should review applications authorized on their account (_User Settings > Authorized Applications_) and remove any that are no longer needed.

## References
- https://github.com/getsentry/sentry/security/advisories/GHSA-hgj4-h2x3-rfx4
- https://nvd.nist.gov/vuln/detail/CVE-2023-39531
- https://github.com/getsentry/sentry
