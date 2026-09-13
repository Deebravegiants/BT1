# [M] Integer underflow in wolfSSL packet sniffer <= 5.8.4 allows an attacker to cause a buffer overflow...

## Summary
Severity: Medium
Advisory: JLSEC-2026-692
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-692
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Integer underflow in wolfSSL packet sniffer <= 5.8.4 allows an attacker to cause a buffer overflow in the AEAD decryption path by injecting a TLS record shorter than the explicit IV plus authentication tag into traffic inspected by `ssl_DecodePacket`. The underflow wraps a 16-bit length to a large value that is passed to AEAD decryption routines, causing heap buffer overflow and a crash. An unauthenticated attacker can trigger this remotely via malformed TLS Application Data records.

## References
- https://github.com/advisories/GHSA-2q9g-q8jj-fr53
- https://github.com/wolfSSL/wolfssl/pull/9571
- https://nvd.nist.gov/vuln/detail/CVE-2026-1005
