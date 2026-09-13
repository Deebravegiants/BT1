# [C] OpenBullet2 0.3.2 Authenticated RCE via Job Configuration Interface

## Summary
Severity: Critical
Advisory: CVE-2026-25856
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-25856
Type: osv

## Details
OpenBullet2 through version 0.3.2 contains an authenticated remote code execution vulnerability that allows authenticated users to execute arbitrary C# code on the server host by creating or modifying job configurations. Attackers can leverage the plain C# execution mode, which lacks reference filtering or API restrictions, to access the file system, spawn processes, and invoke arbitrary .NET APIs as the process user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25856.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25856
- https://www.vulncheck.com/advisories/openbullet2-authenticated-rce-via-job-configuration-interface
- https://github.com/openbullet/openbullet2
- https://hackernoon.com/one-empty-header-to-admin-how-an-auth-bypass-breaks-openbullet2
