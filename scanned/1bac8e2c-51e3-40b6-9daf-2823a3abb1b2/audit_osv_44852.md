# [H] Crypt::DSA versions before 1.20 for Perl generate seeds using rand

## Summary
Severity: High
Advisory: CVE-2026-8700
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-8700
Type: osv

## Details
Crypt::DSA versions before 1.20 for Perl generate seeds using rand.

Seeds were generated using Perl's built-in rand function, which is predictable and unsuitable for security usage.

## References
- http://www.openwall.com/lists/oss-security/2026/05/15/26
- https://cpan.org/modules
- https://metacpan.org/release/TIMLEGGE/Crypt-DSA-1.20/diff/TIMLEGGE/Crypt-DSA-1.19#lib/Crypt/DSA/KeyChain.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8700.json
- https://metacpan.org/release/TIMLEGGE/Crypt-DSA-1.20/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-8700
- https://github.com/perl-Crypt-OpenPGP/Crypt-DSA.git
