# [C] CVE-2019-16748

## Summary
Severity: Critical
Advisory: CVE-2019-16748
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-24
Source: https://osv.dev/vulnerability/CVE-2019-16748
Type: osv

## Details
In wolfSSL through 4.1.0, there is a missing sanity check of memory accesses in parsing ASN.1 certificate data while handshaking. Specifically, there is a one-byte heap-based buffer over-read in CheckCertSignature_ex in wolfcrypt/src/asn.c.

## References
- https://github.com/wolfSSL/wolfssl/issues/2459
