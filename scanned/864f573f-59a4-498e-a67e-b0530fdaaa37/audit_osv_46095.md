# [C] JLSEC-2026-674

## Summary
Severity: Critical
Advisory: JLSEC-2026-674
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-674
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
In wolfSSL before 5.5.2, if callback functions are enabled (via the `WOLFSSL_CALLBACKS` flag), then a malicious TLS 1.3 client or network attacker can trigger a buffer over-read on the heap of 5 bytes. (`WOLFSSL_CALLBACKS` is only intended for debugging.)

## References
- http://packetstormsecurity.com/files/170610/wolfSSL-WOLFSSL_CALLBACKS-Heap-Buffer-Over-Read.html
- http://seclists.org/fulldisclosure/2023/Jan/11
- https://blog.trailofbits.com/2023/01/12/wolfssl-vulnerabilities-tlspuffin-fuzzing-ssh/
- https://github.com/wolfSSL/wolfssl/releases
- https://github.com/wolfSSL/wolfssl/releases/tag/v5.5.2-stable
- https://www.wolfssl.com/docs/security-vulnerabilities/
