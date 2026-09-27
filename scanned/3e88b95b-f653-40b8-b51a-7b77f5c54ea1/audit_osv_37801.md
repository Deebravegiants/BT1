# [H] mod_gnutils has stack-based buffer overflow caused by a long client certificate chain

## Summary
Severity: High
Advisory: CVE-2026-33307
Aliases: GHSA-gjpm-55p4-c76r
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-33307
Type: osv

## Details
Mod_gnutls is a TLS module for Apache HTTPD based on GnuTLS. In versions prior to 0.12.3 and 0.13.0, code for client certificate verification imported the certificate chain sent by the client into a fixed size `gnutls_x509_crt_t x509[]` array without checking the number of certificates is less than or equal to the array size. `gnutls_x509_crt_t` is a `typedef` for a pointer to an opaque GnuTLS structure created using with `gnutls_x509_crt_init()` before importing certificate data into it, so no attacker-controlled data was written into the stack buffer, but writing a pointer after the last array element generally triggered a segfault, and could theoretically cause stack corruption otherwise (not observed in practice). Server configurations that do not use client certificates (`GnuTLSClientVerify ignore`, the default) are not affected. The problem has been fixed in version 0.12.3 by checking the length of the provided certificate chain and rejecting it if it exceeds the buffer length, and in version 0.13.0 by rewriting certificate verification to use `gnutls_certificate_verify_peers()`, removing the need for the buffer entirely. There is no workaround. Version 0.12.3 provides the minimal fix for users of 0.12.x who do not wish to upgrade to 0.13.0 yet.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33307.json
- https://github.com/airtower-luna/mod_gnutls/security/advisories/GHSA-gjpm-55p4-c76r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33307
- https://github.com/airtower-luna/mod_gnutls/commit/bf4f08c49acae528e97885082cdee460f4534dc1
