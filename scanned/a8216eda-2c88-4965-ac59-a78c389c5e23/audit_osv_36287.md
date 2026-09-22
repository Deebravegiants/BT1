# [M] ASN1_TYPE Type Confusion in the PKCS7_digest_from_attributes() function

## Summary
Severity: Medium
Advisory: CVE-2026-22796
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-22796
Type: osv

## Details
Issue summary: A type confusion vulnerability exists in the signature
verification of signed PKCS#7 data where an ASN1_TYPE union member is
accessed without first validating the type, causing an invalid or NULL
pointer dereference when processing malformed PKCS#7 data.

Impact summary: An application performing signature verification of PKCS#7
data or calling directly the PKCS7_digest_from_attributes() function can be
caused to dereference an invalid or NULL pointer when reading, resulting in
a Denial of Service.

The function PKCS7_digest_from_attributes() accesses the message digest attribute
value without validating its type. When the type is not V_ASN1_OCTET_STRING,
this results in accessing invalid memory through the ASN1_TYPE union, causing
a crash.

Exploiting this vulnerability requires an attacker to provide a malformed
signed PKCS#7 to an application that verifies it. The impact of the
exploit is just a Denial of Service, the PKCS7 API is legacy and applications
should be using the CMS API instead. For these reasons the issue was
assessed as Low severity.

The FIPS modules in 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the PKCS#7 parsing implementation is outside the OpenSSL FIPS module
boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0, 1.1.1 and 1.0.2 are vulnerable to this issue.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22796.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22796
- https://openssl-library.org/news/secadv/20260127.txt
- https://github.com/openssl/openssl/commit/2502e7b7d4c0cf4f972a881641fe09edc67aeec4
- https://github.com/openssl/openssl/commit/572844beca95068394c916626a6d3a490f831a49
- https://github.com/openssl/openssl/commit/7bbca05be55b129651d9df4bdb92becc45002c12
- https://github.com/openssl/openssl/commit/eeee3cbd4d682095ed431052f00403004596373e
- https://github.com/openssl/openssl/commit/ef2fb66ec571564d64d1c74a12e388a2a54d05d2
