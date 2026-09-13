# [H] Heap buffer overflow in session parsing with wolfSSL_d2i_SSL_SESSION() function

## Summary
Severity: High
Advisory: CVE-2026-2646
CVSS: 7.5 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-2646
Type: osv

## Details
A heap-buffer-overflow vulnerability exists in wolfSSL's wolfSSL_d2i_SSL_SESSION() function. When deserializing session data with SESSION_CERTS enabled, certificate and session id lengths are read from an untrusted input without bounds validation, allowing an attacker to overflow fixed-size buffers and corrupt heap memory. A maliciously crafted session would need to be loaded from an external source to trigger this vulnerability. Internal sessions were not vulnerable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2646.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2646
- https://github.com/wolfSSL/wolfssl/pull/9748
- https://github.com/wolfSSL/wolfssl/pull/9949
- https://github.com/wolfSSL/wolfssl
