# [H] A heap-buffer-overflow vulnerability exists in wolfSSL's `wolfSSL_d2i_SSL_SESSION()` function

## Summary
Severity: High
Advisory: JLSEC-2026-702
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-702
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
A heap-buffer-overflow vulnerability exists in wolfSSL's `wolfSSL_d2i_SSL_SESSION()` function. When deserializing session data with `SESSION_CERTS` enabled, certificate and session id lengths are read from an untrusted input without bounds validation, allowing an attacker to overflow fixed-size buffers and corrupt heap memory. A maliciously crafted session would need to be loaded from an external source to trigger this vulnerability. Internal sessions were not vulnerable.

## References
- https://github.com/advisories/GHSA-24vq-qfc5-qrmj
- https://github.com/wolfSSL/wolfssl/pull/9748
- https://github.com/wolfSSL/wolfssl/pull/9949
- https://nvd.nist.gov/vuln/detail/CVE-2026-2646
