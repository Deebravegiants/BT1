# [M] h2: Duplicate Host header could facilitate request smuggling

## Summary
Severity: Medium
Advisory: GHSA-6hr6-w5qg-qmwg
CVE: CVE-2026-71554
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-6hr6-w5qg-qmwg
Type: github-advisory

## Affected
- PyPI: `h2` — affected >=0 <4.4.1

## Details
### Impact
h2 <=4.4.0 accepts request header blocks containing more than one Host header, and forwards every Host header to the consuming application. Where the consumer downgrades HTTP/2 to HTTP/1.1, the resulting request carries two Host header lines, which is a request smuggling primitive (CWE-444).

### Patches
Patched and fixed in v4.4.1

### Workarounds
Users of the h2 library are advised to check and follow HTTP semantics best practices in their application code. h2 provides best effort sanity checks, but ultimately the calling code is responsible to ensure proper and safe usage of HTTP/2 as provided by h2, hyperframe, and hpack.

### References
Similar to the previously disclosed and fixed duplicate content-length issue.

## References
- https://github.com/python-hyper/h2/security/advisories/GHSA-6hr6-w5qg-qmwg
- https://github.com/python-hyper/h2/commit/292a40829feefda98c8509dcdbbb4a57af9bd6a6
- https://github.com/python-hyper/h2
