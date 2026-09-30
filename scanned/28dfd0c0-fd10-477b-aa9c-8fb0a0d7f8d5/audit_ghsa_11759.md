# [H] Authentication Bypass in extension "E-Mail MFA Provider" (mfa_email)

## Summary
Severity: High
Advisory: GHSA-29r8-gvx4-r9w3
CVE: CVE-2026-4208
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-29r8-gvx4-r9w3
Type: github-advisory

## Affected
- Packagist: `ralffreit/mfa-email` — affected >=0 <1.0.7
- Packagist: `ralffreit/mfa-email` — affected >=2.0.0 <2.0.1

## Details
The extension fails to properly reset the generated MFA code after successful authentication. This leads to a possible MFA bypass for future login attempts by providing an empty string as MFA code to the extensions MFA provider.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4208
- https://github.com/MrSilaz/mfa_email/commit/0bb7e85b236a5232f7b092915453dd7c3da48f12
- https://github.com/MrSilaz/mfa_email
- https://github.com/MrSilaz/mfa_email/releases/tag/v1.0.7
- https://github.com/MrSilaz/mfa_email/releases/tag/v2.0.1
- https://typo3.org/security/advisory/typo3-ext-sa-2026-007
