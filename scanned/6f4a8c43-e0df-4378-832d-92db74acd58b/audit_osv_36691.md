# [C] n8n is vulnerable to Python sandbox escape

## Summary
Severity: Critical
Advisory: CVE-2026-25115
Aliases: GHSA-8398-gmmx-564h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25115
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to version 2.4.8, a vulnerability in the Python Code node allows authenticated users to break out of the Python sandbox environment and execute code outside the intended security boundary. This issue has been patched in version 2.4.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25115.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-8398-gmmx-564h
- https://nvd.nist.gov/vuln/detail/CVE-2026-25115
