# [H] CVE-2019-18840

## Summary
Severity: High
Advisory: CVE-2019-18840
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-09
Source: https://osv.dev/vulnerability/CVE-2019-18840
Type: osv

## Details
In wolfSSL 4.1.0 through 4.2.0c, there are missing sanity checks of memory accesses in parsing ASN.1 certificate data while handshaking. Specifically, there is a one-byte heap-based buffer overflow inside the DecodedCert structure in GetName in wolfcrypt/src/asn.c because the domain name location index is mishandled. Because a pointer is overwritten, there is an invalid free.

## References
- https://github.com/wolfSSL/wolfssl/issues/2555
