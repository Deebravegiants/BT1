# [C] Crypt::DSA versions before 1.21 for Perl reused the nonce across signatures, leading to private-key recovery

## Summary
Severity: Critical
Advisory: CVE-2026-12205
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-15
Source: https://osv.dev/vulnerability/CVE-2026-12205
Type: osv

## Details
Crypt::DSA versions before 1.21 for Perl reused the nonce across signatures, leading to private-key recovery.

Crypt::DSA::sign caches the per-signature nonce material in the Key object without ever clearing it.

The first sign() on a Key object picks a nonce, and every later sign() on that same object reuses it, producing an identical "r".

Keys used to sign more than once with an affected version should be considered compromised.

## References
- http://www.openwall.com/lists/oss-security/2026/06/15/4
- https://cpan.org/modules
- https://metacpan.org/release/TIMLEGGE/Crypt-DSA-1.20/source/lib/Crypt/DSA.pm#L47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12205.json
- https://metacpan.org/release/TIMLEGGE/Crypt-DSA-1.21/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-12205
- https://github.com/perl-Crypt-OpenPGP/Crypt-DSA
