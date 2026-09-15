# [C] Crypt::OpenSSL::PKCS12 versions through 1.94 for Perl truncates passwords with embedded NULLs

## Summary
Severity: Critical
Advisory: CVE-2026-8721
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-17
Source: https://osv.dev/vulnerability/CVE-2026-8721
Type: osv

## Details
Crypt::OpenSSL::PKCS12 versions through 1.94 for Perl truncates passwords with embedded NULLs.

Password parameters in PKCS12.xs are declared char *, which routes through Perl's default typemap to SvPV_nolen.  The Perl length is discarded.

The C code (or OpenSSL internally) calls strlen() on the buffer.  Any password byte at or after the first NULL is silently dropped. Binary / KDF-derived / HMAC-derived passwords lose entropy without any warnings.

## References
- http://www.openwall.com/lists/oss-security/2026/05/17/6
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8721.json
- https://metacpan.org/release/JONASBN/Crypt-OpenSSL-PKCS12-1.95/view/Changes.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-8721
- https://github.com/dsully/perl-crypt-openssl-pkcs12
