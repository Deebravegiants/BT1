# [C] Crypt::OpenSSL::PKCS12 versions through 1.94 for Perl have out-of-bounds (OOB) write flaws

## Summary
Severity: Critical
Advisory: CVE-2026-8507
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-17
Source: https://osv.dev/vulnerability/CVE-2026-8507
Type: osv

## Details
Crypt::OpenSSL::PKCS12 versions through 1.94 for Perl have out-of-bounds (OOB) write flaws.

When parsing a PKCS12 file, with a >= 1 GiB OCTET STRING (or BIT STRING) attribute on a SAFEBAG, via info() or info_as_hash(), a heap out-of-bounds write would be triggered with remote-code-execution potential (RCE) due to a signed integer overflow in the size calculation passed to Renew().

## References
- http://www.openwall.com/lists/oss-security/2026/05/17/5
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8507.json
- https://metacpan.org/release/JONASBN/Crypt-OpenSSL-PKCS12-1.95/view/Changes.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-8507
- https://github.com/dsully/perl-crypt-openssl-pkcs12/issues/55
- https://github.com/dsully/perl-crypt-openssl-pkcs12/issues/56
- https://github.com/dsully/perl-crypt-openssl-pkcs12/commit/b9d0469c6d8f5b5c6c2a45a3d0647a532b749397.patch
- https://github.com/dsully/perl-crypt-openssl-pkcs12
