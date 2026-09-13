# [H] Snipe-IT has sensitive user attributes related to account privileges that are insufficiently protected against mass assignment

## Summary
Severity: High
Advisory: GHSA-5448-v74m-7mv7
CVE: CVE-2025-15602
CWE: CWE-915
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-5448-v74m-7mv7
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.3.7

## Details
Snipe-IT versions prior to 8.3.7 contain sensitive user attributes related to account privileges that are insufficiently protected against mass assignment. An authenticated, low-privileged user can craft a malicious API request to modify restricted fields of another user account, including the Super Admin account. By changing the email address of the Super Admin and triggering a password reset, an attacker can fully take over the Super Admin account, resulting in complete administrative control of the Snipe-IT instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-15602
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.3.7
- https://snipeitapp.com
- https://www.vulncheck.com/advisories/snipe-it-mass-assignment-vulnerability-leading-to-privilege-escalation
