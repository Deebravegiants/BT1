# [C] Kestra: Remote Code Execution via SQL Injection

## Summary
Severity: Critical
Advisory: CVE-2026-34612
Aliases: CVE-2026-38428, GHSA-365w-2m69-mp9x
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-34612
Type: osv

## Details
Kestra is an open-source, event-driven orchestration platform. Prior to version 1.3.7, Kestra (default docker-compose deployment) contains a SQL Injection vulnerability that leads to Remote Code Execution (RCE) in the following endpoint "GET /api/v1/main/flows/search". Once a user is authenticated, simply visiting a crafted link is enough to trigger the vulnerability. The injected payload is executed by PostgreSQL using COPY ... TO PROGRAM ..., which in turn runs arbitrary OS commands on the host. This issue has been patched in version 1.3.7.

## References
- https://github.com/kestra-io/kestra/releases/tag/v1.3.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34612.json
- https://github.com/kestra-io/kestra/security/advisories/GHSA-365w-2m69-mp9x
- https://nvd.nist.gov/vuln/detail/CVE-2026-34612
- https://github.com/kestra-io/kestra/commit/3926762795df8ad3e03924b370c51832ed3a21d3
