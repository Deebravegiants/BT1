# [H] NEXULEAN API Key Leak

## Summary
Severity: High
Advisory: CVE-2026-32138
Aliases: GHSA-r7cr-5wcx-x9wm
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-03-12
Source: https://osv.dev/vulnerability/CVE-2026-32138
Type: osv

## Details
NEXULEAN is a cybersecurity portfolio & service platform for an Ethical Hacker, AI Enthusiast, and Penetration Tester. Prior to 2.0.0, a security vulnerability was identified where Firebase and Web3Forms API keys were exposed. An attacker could use these keys to interact with backend services without authentication, potentially leading to unauthorized access to application resources and user data. This vulnerability is fixed in 2.0.0.

## References
- https://github.com/Stalin-143/website/releases/tag/v2.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32138.json
- https://github.com/Stalin-143/website/security/advisories/GHSA-r7cr-5wcx-x9wm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32138
