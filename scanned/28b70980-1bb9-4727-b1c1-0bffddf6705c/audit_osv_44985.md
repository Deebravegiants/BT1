# [C] Crypt::OpenSSL::PKCS12 versions before 1.96 for Perl permits a heap OOB read in print_attribute UTF8STRING path

## Summary
Severity: Critical
Advisory: CVE-2026-9265
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-20
Source: https://osv.dev/vulnerability/CVE-2026-9265
Type: osv

## Details
Crypt::OpenSSL::PKCS12 versions before 1.96 for Perl permits a heap OOB read in print_attribute UTF8STRING path.

print_attribute() copies a UTF8STRING ASN.1 attribute value into a heap buffer sized exactly to its declared length via strncpy, leaving no NUL terminator. Downstream callers run strlen() on the result and pass the inflated length to newSVpvn(), copying attacker-influenced adjacent heap bytes into a Perl scalar.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9265.json
- https://metacpan.org/release/JONASBN/Crypt-OpenSSL-PKCS12-1.96/source/Changes.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-9265
- https://github.com/dsully/perl-crypt-openssl-pkcs12/issues/55
- https://github.com/dsully/perl-crypt-openssl-pkcs12/commit/a7bd2f319fa8aab8177b3d767ea06dd85ceb3173.patch
- https://github.com/dsully/perl-crypt-openssl-pkcs12
