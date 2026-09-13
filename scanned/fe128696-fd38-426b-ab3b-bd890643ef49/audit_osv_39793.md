# [C] Crypt::SaltedHash versions through 0.09 for Perl generate insecure random values for salts

## Summary
Severity: Critical
Advisory: CVE-2026-47372
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-47372
Type: osv

## Details
Crypt::SaltedHash versions through 0.09 for Perl generate insecure random values for salts.

These versions use the built-in rand function, which is predictable and unsuitable for cryptography.

## References
- http://www.openwall.com/lists/oss-security/2026/05/20/22
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47372.json
- https://metacpan.org/release/RRWO/Crypt-SaltedHash-0.10/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-47372
- https://github.com/robrwo/perl-Crypt-SaltedHash/commit/9b68437d2cd420b819b3a795474c3870338d38d5.patch
- https://github.com/robrwo/perl-Crypt-SaltedHash
