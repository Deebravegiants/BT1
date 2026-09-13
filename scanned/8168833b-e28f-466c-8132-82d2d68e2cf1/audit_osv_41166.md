# [C] Crypt::OpenSSL::X509 versions before 2.1.3 for Perl allow a heap out-of-bounds read via a long certificate extension OID in hv_exts

## Summary
Severity: Critical
Advisory: CVE-2026-58102
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-58102
Type: osv

## Details
Crypt::OpenSSL::X509 versions before 2.1.3 for Perl allow a heap out-of-bounds read via a long certificate extension OID in hv_exts.

When building the extension hash (via extensions(), extensions_by_long_name(), extensions_by_oid(), or has_extension_oid()), the code passes OBJ_obj2txt()'s return value as the hash-key length; because that value is the OID's full text length rather than the bytes written to the fixed-size buffer (129 bytes), an OID whose text is longer than the 129-byte buffer causes a read past the allocation, exposing adjacent heap memory as the returned hash key. extensions_by_name() uses the static shortname path and is not affected.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58102.json
- https://metacpan.org/release/JONASBN/Crypt-OpenSSL-X509-2.1.3/source/Changes.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-58102
- https://github.com/dsully/perl-crypt-openssl-x509/commit/757289bfce095455c104d4adfe9312e7b339620f.patch
- https://github.com/dsully/perl-crypt-openssl-x509
