# [H] ALPINE-CVE-2022-4450

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-4450
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-4450
Type: osv

## Affected
- Alpine:v3.14: `openssl` — affected >=1.1.1 <1.1.1t-r0
- Alpine:v3.15: `openssl` — affected >=1.1.1 <1.1.1t-r0
- Alpine:v3.16: `openssl` — affected >=1.1.1 <1.1.1t-r0
- Alpine:v3.17: `openssl` — affected >=1.1.1 <3.0.8-r0
- Alpine:v3.18: `openssl` — affected >=1.1.1 <3.0.8-r0
- Alpine:v3.19: `openssl` — affected >=1.1.1 <3.0.8-r0
- Alpine:v3.20: `openssl` — affected >=1.1.1 <3.0.8-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1 <3.0.8-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1 <3.0.8-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1 <3.0.8-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1 <3.0.8-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.8-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.8-r0

## Details
The function PEM_read_bio_ex() reads a PEM file from a BIO and parses and
decodes the "name" (e.g. "CERTIFICATE"), any header data and the payload data.
If the function succeeds then the "name_out", "header" and "data" arguments are
populated with pointers to buffers containing the relevant decoded data. The
caller is responsible for freeing those buffers. It is possible to construct a
PEM file that results in 0 bytes of payload data. In this case PEM_read_bio_ex()
will return a failure code but will populate the header argument with a pointer
to a buffer that has already been freed. If the caller also frees this buffer
then a double free will occur. This will most likely lead to a crash. This
could be exploited by an attacker who has the ability to supply malicious PEM
files for parsing to achieve a denial of service attack.

The functions PEM_read_bio() and PEM_read() are simple wrappers around
PEM_read_bio_ex() and therefore these functions are also directly affected.

These functions are also called indirectly by a number of other OpenSSL
functions including PEM_X509_INFO_read_bio_ex() and
SSL_CTX_use_serverinfo_file() which are also vulnerable. Some OpenSSL internal
uses of these functions are not vulnerable because the caller does not free the
header argument if PEM_read_bio_ex() returns a failure code. These locations
include the PEM_read_bio_TYPE() functions as well as the decoders introduced in
OpenSSL 3.0.

The OpenSSL asn1parse command line application is also impacted by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-4450
