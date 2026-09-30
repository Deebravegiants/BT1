# [H] Perl's Crypt::Random module after 1.05 and before 1.56 may use rand() function for cryptographic functions

## Summary
Severity: High
Advisory: CVE-2025-1828
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-03-10
Source: https://osv.dev/vulnerability/CVE-2025-1828
Type: osv

## Details
Crypt::Random Perl package 1.05 through 1.55 may use rand() function, which is not cryptographically strong, for cryptographic functions.

If the Provider is not specified and /dev/urandom or an Entropy Gathering Daemon (egd) service is not available Crypt::Random will default to use the insecure Crypt::Random::rand provider.

In particular, Windows versions of perl will encounter this issue by default.

## References
- https://perldoc.perl.org/functions/rand
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1828.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1828
- https://github.com/perl-Crypt-OpenPGP/Crypt-Random/commit/1f8b29e9e89d8d083fd025152e76ec918136cc05
- https://github.com/perl-Crypt-OpenPGP/Crypt-Random/pull/1
