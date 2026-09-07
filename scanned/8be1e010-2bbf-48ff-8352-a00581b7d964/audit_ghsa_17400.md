# [H] Universal Tool Calling Protocol (UTCP) client library for Python vulnerable to Trust Boundary Violation through Manual JSON specification

## Summary
Severity: High
Advisory: GHSA-75mj-4g74-9rg2
CVE: CVE-2025-14542
CWE: CWE-501
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-13
Source: https://github.com/advisories/GHSA-75mj-4g74-9rg2
Type: github-advisory

## Affected
- PyPI: `utcp` — affected >=0 <1.1.0

## Details
The vulnerability arises when a client fetches a tools’ JSON specification, known as a Manual, from a remote Manual Endpoint. While a provider may initially serve a benign manual (e.g., one defining an HTTP tool call), earning the clients’ trust, a malicious provider can later change the manual to exploit the client.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14542
- https://github.com/universal-tool-calling-protocol/python-utcp/commit/2dc9c02df72cad3770c934959325ec344b441444
- https://github.com/universal-tool-calling-protocol/python-utcp
- https://research.jfrog.com/vulnerabilities/python-utcp-untrusted-manual-command-execution-jfsa-2025-001648329
