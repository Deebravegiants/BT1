# [M] Integer underflow in wolfSSL packet sniffer <= 5.9.0 allows an attacker to cause a program crash in...

## Summary
Severity: Medium
Advisory: JLSEC-2026-741
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-741
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Integer underflow in wolfSSL packet sniffer <= 5.9.0 allows an attacker to cause a program crash in the AEAD decryption path by injecting a TLS record shorter than the explicit IV plus authentication tag into traffic inspected by `ssl_DecodePacket`. The underflow wraps a 16-bit length to a large value that is passed to AEAD decryption routines, causing a large out-of-bounds read and crash. An unauthenticated attacker can trigger this remotely via malformed TLS Application Data records.

## References
- https://github.com/advisories/GHSA-2jvp-h4w4-2vxh
- https://github.com/wolfSSL/wolfssl/pull/10125
- https://nvd.nist.gov/vuln/detail/CVE-2026-5778
