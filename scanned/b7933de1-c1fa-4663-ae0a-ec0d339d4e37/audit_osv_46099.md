# [C] In wolfSSL prior to 5.6.6, if callback functions are enabled (via the `WOLFSSL_CALLBACKS` flag),...

## Summary
Severity: Critical
Advisory: JLSEC-2026-678
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-678
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
In wolfSSL prior to 5.6.6, if callback functions are enabled (via the `WOLFSSL_CALLBACKS` flag), then a malicious TLS client or network attacker can trigger a buffer over-read on the heap of 5 bytes (`WOLFSSL_CALLBACKS` is only intended for debugging).

## References
- https://github.com/advisories/GHSA-cwpg-8775-j56v
- https://github.com/wolfSSL/wolfssl/pull/6949
- https://github.com/wolfSSL/wolfssl/pull/6949/
- https://nvd.nist.gov/vuln/detail/CVE-2023-6936
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
