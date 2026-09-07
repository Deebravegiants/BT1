# [M] Null pointer dereference in PKCS12 parsing

## Summary
Severity: Medium
Advisory: GHSA-9v9h-cgj8-h64p
CVE: CVE-2024-0727
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-26
Source: https://github.com/advisories/GHSA-9v9h-cgj8-h64p
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=0 <42.0.2

## Details
Issue summary: Processing a maliciously formatted PKCS12 file may lead OpenSSL
to crash leading to a potential Denial of Service attack

Impact summary: Applications loading files in the PKCS12 format from untrusted
sources might terminate abruptly.

A file in PKCS12 format can contain certificates and keys and may come from an
untrusted source. The PKCS12 specification allows certain fields to be NULL, but
OpenSSL does not correctly check for this case. This can lead to a NULL pointer
dereference that results in OpenSSL crashing. If an application processes PKCS12
files from an untrusted source using the OpenSSL APIs then that application will
be vulnerable to this issue.

OpenSSL APIs that are vulnerable to this are: PKCS12_parse(),
PKCS12_unpack_p7data(), PKCS12_unpack_p7encdata(), PKCS12_unpack_authsafes()
and PKCS12_newpass().

We have also fixed a similar issue in SMIME_write_PKCS7(). However since this
function is related to writing data we do not consider it security significant.

The FIPS modules in 3.2, 3.1 and 3.0 are not affected by this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0727
- https://github.com/github/advisory-database/pull/3472
- https://github.com/openssl/openssl/pull/23362
- https://github.com/alexcrichton/openssl-src-rs/commit/add20f73b6b42be7451af2e1044d4e0e778992b2
- https://github.com/openssl/openssl/commit/09df4395b5071217b76dc7d3d2e630eb8c5a79c2
- https://github.com/openssl/openssl/commit/775acfdbd0c6af9ac855f34969cdab0c0c90844a
- https://github.com/openssl/openssl/commit/d135eeab8a5dbf72b3da5240bab9ddb7678dbd2c
- https://github.com/pyca/cryptography/commit/3519591d255d4506fbcd0d04037d45271903c64d
- https://www.openssl.org/news/secadv/20240125.txt
- https://security.netapp.com/advisory/ntap-20240208-0006
- https://lists.debian.org/debian-lts-announce/2024/11/msg00000.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00033.html
- https://github.openssl.org/openssl/extended-releases/commit/aebaa5883e31122b404e450732dc833dc9dee539
- https://github.openssl.org/openssl/extended-releases/commit/03b3941d60c4bce58fab69a0c22377ab439bc0e8
- https://cert-portal.siemens.com/productcert/html/ssa-915275.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://cert-portal.siemens.com/productcert/html/ssa-331112.html
- https://cert-portal.siemens.com/productcert/html/ssa-277137.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- http://www.openwall.com/lists/oss-security/2024/03/11/1
