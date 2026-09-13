# [H] Authen::TOTP versions before 0.1.1 for Perl generate secrets using rand

## Summary
Severity: High
Advisory: CVE-2026-46473
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-46473
Type: osv

## Details
Authen::TOTP versions before 0.1.1 for Perl generate secrets using rand.

Secrets were generated using Perl's built-in rand function, which is predictable and unsuitable for security usage.

## References
- http://www.openwall.com/lists/oss-security/2026/05/21/15
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46473.json
- https://metacpan.org/release/TCHATZI/Authen-TOTP-0.1.1/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-46473
- https://github.com/tchatzi/Authen-TOTP/commit/d04f30cc6538d77fc6b6d550da450cf3017b8561.patch
- https://github.com/tchatzi/Authen-TOTP
