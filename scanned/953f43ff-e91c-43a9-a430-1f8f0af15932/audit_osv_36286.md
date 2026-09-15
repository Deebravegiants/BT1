# [M] Missing ASN1_TYPE validation in PKCS#12 parsing

## Summary
Severity: Medium
Advisory: CVE-2026-22795
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-22795
Type: osv

## Details
Issue summary: An invalid or NULL pointer dereference can happen in
an application processing a malformed PKCS#12 file.

Impact summary: An application processing a malformed PKCS#12 file can be
caused to dereference an invalid or NULL pointer on memory read, resulting
in a Denial of Service.

A type confusion vulnerability exists in PKCS#12 parsing code where
an ASN1_TYPE union member is accessed without first validating the type,
causing an invalid pointer read.

The location is constrained to a 1-byte address space, meaning any
attempted pointer manipulation can only target addresses between 0x00 and 0xFF.
This range corresponds to the zero page, which is unmapped on most modern
operating systems and will reliably result in a crash, leading only to a
Denial of Service. Exploiting this issue also requires a user or application
to process a maliciously crafted PKCS#12 file. It is uncommon to accept
untrusted PKCS#12 files in applications as they are usually used to store
private keys which are trusted by definition. For these reasons, the issue
was assessed as Low severity.

The FIPS modules in 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the PKCS12 implementation is outside the OpenSSL FIPS module boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0 and 1.1.1 are vulnerable to this issue.

OpenSSL 1.0.2 is not affected by this issue.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22795.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22795
- https://openssl-library.org/news/secadv/20260127.txt
- https://github.com/openssl/openssl/commit/2502e7b7d4c0cf4f972a881641fe09edc67aeec4
- https://github.com/openssl/openssl/commit/572844beca95068394c916626a6d3a490f831a49
- https://github.com/openssl/openssl/commit/7bbca05be55b129651d9df4bdb92becc45002c12
- https://github.com/openssl/openssl/commit/eeee3cbd4d682095ed431052f00403004596373e
- https://github.com/openssl/openssl/commit/ef2fb66ec571564d64d1c74a12e388a2a54d05d2
