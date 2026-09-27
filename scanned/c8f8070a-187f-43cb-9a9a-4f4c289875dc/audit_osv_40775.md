# [M] Tinyproxy - Stathost Detection Bypass via Host Header Manipulation

## Summary
Severity: Medium
Advisory: CVE-2026-55202
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-55202
Type: osv

## Details
Tinyproxy through 1.11.3, fixed in commit 09312a1, fails to properly validate the Host header during stathost detection, allowing unauthenticated attackers to access the stats page by injecting a matching Host header or bypass detection via port manipulation. Remote attackers can trigger unauthorized access to internal proxy statistics or misroute requests as transparent proxy connections to circumvent access controls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55202.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55202
- https://www.vulncheck.com/advisories/evil-winrm-path-traversal-in-download-dir-function
- https://github.com/tinyproxy/tinyproxy/pull/606
- https://github.com/tinyproxy/tinyproxy/commit/09312a185ae25cc486b4ff5987638a7917a48bce
- https://github.com/tinyproxy/tinyproxy
