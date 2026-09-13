# [H] Tornado has an HTTP cookie parsing DoS vulnerability

## Summary
Severity: High
Advisory: GHSA-8w49-h785-mj3c
CVE: CVE-2024-52804
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-22
Source: https://github.com/advisories/GHSA-8w49-h785-mj3c
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.4.2

## Details
The algorithm used for parsing HTTP cookies in Tornado versions prior to 6.4.2 sometimes has quadratic complexity, leading to excessive CPU consumption when parsing maliciously-crafted cookie headers. This parsing occurs in the event loop thread and may block the processing of other requests.

See also CVE-2024-7592 for a similar vulnerability in cpython.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-8w49-h785-mj3c
- https://nvd.nist.gov/vuln/detail/CVE-2024-52804
- https://github.com/tornadoweb/tornado/commit/d5ba4a1695fbf7c6a3e54313262639b198291533
- https://github.com/tornadoweb/tornado
- https://lists.debian.org/debian-lts-announce/2025/01/msg00000.html
