# [H] immich API Key Privilege Escalation vulnerability

## Summary
Severity: High
Advisory: CVE-2026-23896
Aliases: GHSA-237r-x578-h5mv
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-23896
Type: osv

## Details
immich is a high performance self-hosted photo and video management solution. Prior to version 2.5.0, API keys can escalate their own permissions by calling the update endpoint, allowing a low-privilege API key to grant itself full administrative access to the system. Version 2.5.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23896.json
- https://github.com/immich-app/immich/security/advisories/GHSA-237r-x578-h5mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-23896
