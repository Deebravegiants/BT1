# [M] ALPINE-CVE-2024-0727

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-0727
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-0727
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.12-r4
- Alpine:v3.18: `openssl` — affected >=1.0.2 <3.1.4-r5
- Alpine:v3.19: `openssl` — affected >=1.0.2 <3.1.4-r5
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.1.4-r5
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.1.4-r5
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.1.4-r5
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.1.4-r5
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.1.4-r5

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
- https://security.alpinelinux.org/vuln/CVE-2024-0727
