# [M] A certificate verification error in wolfSSL when building with the `WOLFSSL_SYS_CA_CERTS` and...

## Summary
Severity: Medium
Advisory: JLSEC-2026-690
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:Y/R:X/V:D/RE:X/U:Red)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-690
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.7.2+0 <5.8.4+0

## Details
A certificate verification error in wolfSSL when building with the `WOLFSSL_SYS_CA_CERTS` and `WOLFSSL_APPLE_NATIVE_CERT_VALIDATION` options results in the wolfSSL
client failing to properly verify the server certificate's domain name,
allowing any certificate issued by a trusted CA to be accepted regardless of the hostname.

## References
- http://github.com/wolfssl/wolfssl.git
- https://github.com/advisories/GHSA-g6x8-5jj7-qqfv
- https://nvd.nist.gov/vuln/detail/CVE-2025-7395
