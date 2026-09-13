# [C] CVE-2019-15651

## Summary
Severity: Critical
Advisory: CVE-2019-15651
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-26
Source: https://osv.dev/vulnerability/CVE-2019-15651
Type: osv

## Details
wolfSSL 4.1.0 has a one-byte heap-based buffer over-read in DecodeCertExtensions in wolfcrypt/src/asn.c because reading the ASN_BOOLEAN byte is mishandled for a crafted DER certificate in GetLength_ex.

## References
- https://github.com/wolfSSL/wolfssl/issues/2421
