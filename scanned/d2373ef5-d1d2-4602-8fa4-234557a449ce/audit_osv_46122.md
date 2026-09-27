# [M] JLSEC-2026-701

## Summary
Severity: Medium
Advisory: JLSEC-2026-701
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-701
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.8.4+0

## Details
In wolfSSL 5.8.2 and earlier, a logic flaw existed in the TLS 1.2 server state machine implementation. The server could incorrectly accept the CertificateVerify message before the ClientKeyExchange message had been received. This issue affects wolfSSL before 5.8.4 (wolfSSL 5.8.2 and earlier is vulnerable, 5.8.4 is not vulnerable). In 5.8.4 wolfSSL would detect the issue later in the handshake. 5.9.0 was further hardened to catch the issue earlier in the handshake.

## References
- https://github.com/wolfSSL/wolfssl/pull/9694
