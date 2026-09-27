# [H] JLSEC-2026-673

## Summary
Severity: High
Advisory: JLSEC-2026-673
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-673
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
In wolfSSL before 5.5.1, malicious clients can cause a buffer overflow during a TLS 1.3 handshake. This occurs when an attacker supposedly resumes a previous TLS session. During the resumption Client Hello a Hello Retry Request must be triggered. Both Client Hellos are required to contain a list of duplicate cipher suites to trigger the buffer overflow. In total, two Client Hellos have to be sent: one in the resumed session, and a second one as a response to a Hello Retry Request message.

## References
- http://packetstormsecurity.com/files/169600/wolfSSL-Buffer-Overflow.html
- http://seclists.org/fulldisclosure/2022/Oct/24
- https://blog.trailofbits.com/2023/01/12/wolfssl-vulnerabilities-tlspuffin-fuzzing-ssh/
- https://github.com/wolfSSL/wolfssl/releases
- https://www.wolfssl.com/docs/security-vulnerabilities/
