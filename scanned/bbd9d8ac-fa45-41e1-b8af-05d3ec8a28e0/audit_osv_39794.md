# [H] Crypt::SaltedHash versions through 0.09 for Perl is susceptible to timing attacks

## Summary
Severity: High
Advisory: CVE-2026-47373
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-47373
Type: osv

## Details
Crypt::SaltedHash versions through 0.09 for Perl is susceptible to timing attacks.

These versions use Perl's built-in eq comparison. Discrepencies in timing could be used to guess the underlying hash.

## References
- http://www.openwall.com/lists/oss-security/2026/05/20/21
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47373.json
- https://metacpan.org/release/RRWO/Crypt-SaltedHash-0.10/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-47373
- https://github.com/robrwo/perl-Crypt-SaltedHash/commit/c07bfc5c23185b0667233d0f2e1252d81f1f027a.patch
- https://github.com/robrwo/perl-Crypt-SaltedHash
