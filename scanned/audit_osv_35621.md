# [M] Missing SNI/ALPN binding on stateful (session-ID) TLS session resumption

## Summary
Severity: Medium
Advisory: CVE-2026-11703
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-11703
Type: osv

## Details
Missing SNI/ALPN binding on stateful (session-ID) resumption, which previously skipped the binding check performed for ticket-based resumption. A cached session could be resumed under a different SNI/ALPN than originally negotiated and, where client-authentication policy differs across virtual hosts, carry the cached peer-authentication state into a context it was not established for. Resumption now verifies the SNI/ALPN binding for all paths and declines (falling back to a full handshake) on mismatch.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11703.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11703
- https://github.com/wolfSSL/wolfssl/pull/10489
- https://github.com/wolfSSL/wolfssl
