# [M] ECH parsing heap buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2026-3549
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:H/SC:L/SI:L/SA:L)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-3549
Type: osv

## Details
Heap Overflow in TLS 1.3 ECH parsing. An integer underflow existed in ECH extension parsing logic when calculating a buffer length, which resulted in writing beyond the bounds of an allocated buffer. Note that in wolfSSL, ECH is off by default, and the ECH standard is still evolving.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3549.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3549
- https://github.com/wolfSSL/wolfssl/pull/9817
