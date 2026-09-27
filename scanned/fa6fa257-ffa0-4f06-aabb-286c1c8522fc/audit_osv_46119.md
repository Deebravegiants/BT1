# [M] Missing SNI/ALPN binding on stateful (session-ID) resumption, which previously skipped the binding...

## Summary
Severity: Medium
Advisory: JLSEC-2026-698
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-698
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Missing SNI/ALPN binding on stateful (session-ID) resumption, which previously skipped the binding check performed for ticket-based resumption. A cached session could be resumed under a different SNI/ALPN than originally negotiated and, where client-authentication policy differs across virtual hosts, carry the cached peer-authentication state into a context it was not established for. Resumption now verifies the SNI/ALPN binding for all paths and declines (falling back to a full handshake) on mismatch.

## References
- https://github.com/advisories/GHSA-q3px-vrjj-4f97
- https://github.com/wolfSSL/wolfssl/pull/10489
- https://nvd.nist.gov/vuln/detail/CVE-2026-11703
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
