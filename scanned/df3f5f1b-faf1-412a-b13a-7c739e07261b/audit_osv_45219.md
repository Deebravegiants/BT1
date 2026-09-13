# [H] Integer Overflow vulnerability in Mbed TLS 2.x before 2.28.7 and 3.x before 3.5.2, allows attackers...

## Summary
Severity: High
Advisory: JLSEC-2025-224
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-224
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.28.10+0

## Details
Integer Overflow vulnerability in Mbed TLS 2.x before 2.28.7 and 3.x before 3.5.2, allows attackers to cause a denial of service (DoS) via `mbedtls_x509_set_extension()`.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GP5UU7Z6LJNBLBT4SC5WWS2HDNMTFZH5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IIBPEYSVRK4IFLBSYJAWKH33YBNH5HR2/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GP5UU7Z6LJNBLBT4SC5WWS2HDNMTFZH5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IIBPEYSVRK4IFLBSYJAWKH33YBNH5HR2/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2024-01-2/
