# [C] wolfSSL Python module vulnerable to Improper Authentication

## Summary
Severity: Critical
Advisory: GHSA-vj87-jj27-4h9c
CVE: CVE-2025-15346
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-vj87-jj27-4h9c
Type: github-advisory

## Affected
- PyPI: `wolfssl` — affected >=0 <5.8.4.post0

## Details
A vulnerability in the handling of verify_mode = CERT_REQUIRED in the wolfssl Python package (wolfssl-py) causes client certificate requirements to not be fully enforced. 

Because the WOLFSSL_VERIFY_FAIL_IF_NO_PEER_CERT flag was not included, the behavior effectively matched CERT_OPTIONAL: a peer certificate was verified if presented, but connections were incorrectly authenticated when no client certificate was provided. 

This results in improper authentication, allowing attackers to bypass mutual TLS (mTLS) client authentication by omitting a client certificate during the TLS handshake. 

The issue affects versions up to and including 5.8.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-15346
- https://github.com/wolfSSL/wolfssl-py/pull/62
- https://github.com/wolfSSL/wolfssl-py/commit/b4517dece79f682a8f453abce5cfc0b81bae769d
- https://github.com/wolfSSL/wolfssl-py
- https://github.com/wolfSSL/wolfssl-py/releases/tag/v5.8.4-stable
