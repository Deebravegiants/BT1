# [M] Acceptance of CertificateVerify Message before ClientKeyExchange in TLS 1.2

## Summary
Severity: Medium
Advisory: CVE-2026-2645
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-2645
Type: osv

## Details
In wolfSSL 5.8.2 and earlier, a logic flaw existed in the TLS 1.2 server state machine implementation. The server could incorrectly accept the CertificateVerify message before the ClientKeyExchange message had been received. This issue affects wolfSSL before 5.8.4 (wolfSSL 5.8.2 and earlier is vulnerable, 5.8.4 is not vulnerable). In 5.8.4 wolfSSL would detect the issue later in the handshake. 5.9.0 was further hardened to catch the issue earlier in the handshake.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2645.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2645
- https://github.com/wolfSSL/wolfssl/pull/9694
