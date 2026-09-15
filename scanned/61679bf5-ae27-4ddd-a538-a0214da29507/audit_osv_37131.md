# [M] elabftw allows MFA bypass during login

## Summary
Severity: Medium
Advisory: CVE-2026-28510
Aliases: GHSA-x5wv-c9q4-fj65
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-28510
Type: osv

## Details
eLabFTW is an open source electronic lab notebook. In elabftw versions through 5.4.1, the login flow did not reliably preserve the multi-factor authentication state across authentication steps. Under certain conditions, an attacker with valid primary credentials could complete authentication with an attacker-controlled TOTP secret and bypass the additional factor. This could result in unauthorized account access. This issue is fixed in version 5.4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28510.json
- https://github.com/elabftw/elabftw/security/advisories/GHSA-x5wv-c9q4-fj65
- https://nvd.nist.gov/vuln/detail/CVE-2026-28510
- https://github.com/elabftw/elabftw/commit/8b7a575aef128870861187eaa2b2f0f08654ecf9
