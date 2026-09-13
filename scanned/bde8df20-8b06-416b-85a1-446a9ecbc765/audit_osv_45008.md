# [H] Crypt::PBKDF2 versions before 0.261630 for Perl generate insecure random values for salts

## Summary
Severity: High
Advisory: CVE-2026-9638
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-9638
Type: osv

## Details
Crypt::PBKDF2 versions before 0.261630 for Perl generate insecure random values for salts.

These versions use the built-in rand function, which is predictable and unsuitable for cryptography.

## References
- http://www.openwall.com/lists/oss-security/2026/06/12/4
- https://cpan.org/modules
- https://metacpan.org/dist/Crypt-PBKDF2/source/lib/Crypt/PBKDF2.pm#L86-93
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9638.json
- https://metacpan.org/release/ARODLAND/Crypt-PBKDF2-0.261630/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-9638
- https://github.com/arodland/Crypt-PBKDF2
