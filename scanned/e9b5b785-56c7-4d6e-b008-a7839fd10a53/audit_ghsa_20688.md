# [C] Cockpit before 2.2.0 vulnerable to Insufficient Session Expiration

## Summary
Severity: Critical
Advisory: GHSA-vm6p-35rw-3fxc
CVE: CVE-2022-2713
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-09
Source: https://github.com/advisories/GHSA-vm6p-35rw-3fxc
Type: github-advisory

## Affected
- Packagist: `aheinze/cockpit` — affected >=0 <2.2.0

## Details
Cockpit before version 2.2.0 is vulnerable to Insufficient Session Expiration. The application does not validate requests after password changes, allowing a user to change their account details even after an admin changes their password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2713
- https://github.com/cockpit-hq/cockpit/commit/dd8d0314912fa6517ebd2cc9939d9fafbe68731b
- https://github.com/cockpit-hq/cockpit
- https://huntr.dev/bounties/3080fc96-75d7-4868-84de-9fc8c9b90290
