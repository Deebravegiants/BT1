# [H] Crypt::OpenSSL::X509 versions before 2.1.3 for Perl allow denial of service via NULL pointer dereference

## Summary
Severity: High
Advisory: CVE-2026-58101
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-58101
Type: osv

## Details
Crypt::OpenSSL::X509 versions before 2.1.3 for Perl allow denial of service via NULL pointer dereference.

X509V3_EXT_d2i(ext) returns NULL when an extension's DER value fails to parse. basicC, ia5string, and auth_att dereference its result without a NULL check. keyid_data also dereferences akid->keyid, which is NULL for an empty AKI SEQUENCE (DER 30 00) even when the parse succeeds.

A caller invoking an affected helper on an extension from an untrusted certificate triggers a SIGSEGV that crashes the Perl process.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58101.json
- https://metacpan.org/release/JONASBN/Crypt-OpenSSL-X509-2.1.3/source/Changes.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-58101
- https://github.com/dsully/perl-crypt-openssl-x509/commit/4c1e2370556097c253ae27abe9e1097ea377fbd2.patch
- https://github.com/dsully/perl-crypt-openssl-x509
