# [C] Windmill < 1.603.3 File Ownership Handling SQLi RCE

## Summary
Severity: Critical
Advisory: CVE-2026-23696
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-23696
Type: osv

## Details
Windmill CE and EE versions 1.276.0 through 1.603.2 contain an SQL injection vulnerability in the folder ownership management functionality that allows authenticated attackers to inject SQL through the owner parameter. An attacker can use the injection to read sensitive data such as the JWT signing secret and administrative user identifiers, forge an administrative token, and then execute arbitrary code via the workflow execution endpoints.

## References
- https://www.windmill.dev/
- https://apps.nextcloud.com/apps/flow/releases
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23696.json
- https://github.com/windmill-labs/windmill/releases/tag/v1.603.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-23696
- https://www.vulncheck.com/advisories/windmill-file-ownership-handling-sqli-rce
- https://github.com/windmill-labs/windmill/commit/942fb629210ebb287f48467d1535ffde3a3eeafe
- https://github.com/windmill-labs/windmill
- https://chocapikk.com/posts/2026/windfall-nextcloud-flow-windmill-rce/
- https://github.com/Chocapikk/Windfall
