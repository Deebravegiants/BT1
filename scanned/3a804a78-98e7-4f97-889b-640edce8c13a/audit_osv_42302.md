# [H] Crypt::PasswdMD5 versions through 1.42 for Perl generates insecure random values for salts

## Summary
Severity: High
Advisory: CVE-2026-6659
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-6659
Type: osv

## Details
Crypt::PasswdMD5 versions through 1.42 for Perl generates insecure random values for salts.

The built-in rand function is predictable, and unsuitable for cryptography.

## References
- http://www.openwall.com/lists/oss-security/2026/05/08/17
- https://cpan.org/modules
- https://metacpan.org/release/RSAVAGE/Crypt-PasswdMD5-1.42/source/lib/Crypt/PasswdMD5.pm#L35-47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6659.json
- https://metacpan.org/release/RSAVAGE/Crypt-PasswdMD5-1.43/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-6659
- https://github.com/ronsavage/Crypt-PasswdMD5/pull/3
- https://github.com/ronsavage/Crypt-PasswdMD5/commit/a2f821637db0296082297aa4b02254ab08f0dc5e.patch
- https://github.com/ronsavage/Crypt-PasswdMD5
