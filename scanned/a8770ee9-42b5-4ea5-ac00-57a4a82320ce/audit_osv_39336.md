# [C] Heym < 0.0.21 Sandbox Escape via Python Introspection

## Summary
Severity: Critical
Advisory: CVE-2026-45227
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-45227
Type: osv

## Details
Heym before 0.0.21 contains a sandbox escape vulnerability in the custom Python tool executor that allows authenticated workflow authors to bypass sandbox restrictions by using object-graph introspection primitives. Attackers can use Python introspection techniques to recover the unrestricted __import__ function, import blocked modules such as os and subprocess, and access inherited backend environment variables containing database credentials and encryption keys to execute arbitrary host commands as the backend service user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45227.json
- https://github.com/heymrun/heym/releases/tag/v0.0.21
- https://nvd.nist.gov/vuln/detail/CVE-2026-45227
- https://www.vulncheck.com/advisories/heym-sandbox-escape-via-python-introspection
- https://github.com/heymrun/heym/pull/94
- https://github.com/heymrun/heym/commit/32b7e809d987d9b018ec8daa2cdaf48f627f26f1
- https://github.com/heymrun/heym
