# [H] JLSEC-2026-672

## Summary
Severity: High
Advisory: JLSEC-2026-672
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-672
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
An issue was discovered in wolfSSL before 5.5.0. When a TLS 1.3 client connects to a wolfSSL server and `SSL_clear` is called on its session, the server crashes with a segmentation fault. This occurs in the second session, which is created through TLS session resumption and reuses the initial struct WOLFSSL. If the server reuses the previous session structure (struct WOLFSSL) by calling `wolfSSL_clear`(WOLFSSL* ssl) on it, the next received Client Hello (that resumes the previous session) crashes the server. Note that this bug is only triggered when resuming sessions using TLS session resumption. Only servers that use `wolfSSL_clear` instead of the recommended `SSL_free`; `SSL_new` sequence are affected. Furthermore, `wolfSSL_clear` is part of wolfSSL's compatibility layer and is not enabled by default. It is not part of wolfSSL's native API.

## References
- http://packetstormsecurity.com/files/170604/wolfSSL-Session-Resumption-Denial-Of-Service.html
- http://seclists.org/fulldisclosure/2023/Jan/7
- https://blog.trailofbits.com/2023/01/12/wolfssl-vulnerabilities-tlspuffin-fuzzing-ssh/
- https://github.com/tlspuffin/tlspuffin
- https://github.com/wolfSSL/wolfssl/pull/5468
- https://github.com/wolfSSL/wolfssl/releases
- https://www.wolfssl.com/docs/security-vulnerabilities/
