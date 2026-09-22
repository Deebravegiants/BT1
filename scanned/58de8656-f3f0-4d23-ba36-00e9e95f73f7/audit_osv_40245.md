# [H] DTLS 1.3 ACK heap buffer overflow

## Summary
Severity: High
Advisory: CVE-2026-5264
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-5264
Type: osv

## Details
Heap buffer overflow in DTLS 1.3 ACK message processing. A remote attacker can send a crafted DTLS 1.3 ACK message that triggers a heap buffer overflow.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5264.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5264
- https://github.com/wolfssl/wolfssl/pull/10076
- https://github.com/wolfSSL/wolfssl
