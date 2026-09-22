# [H] Metersphere has SQL Injection Vulnerability in Sorting Field

## Summary
Severity: High
Advisory: CVE-2025-53639
Aliases: GHSA-vcm3-5w3f-9f45
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-07-14
Source: https://osv.dev/vulnerability/CVE-2025-53639
Type: osv

## Details
MeterSphere is an open source continuous testing platform. Prior to version 3.6.5-lts, the sortField parameter in certain API endpoints is not properly validated or sanitized. An attacker can supply crafted input to inject and execute arbitrary SQL statements through the sorting functionality. This could result in modification or deletion of database contents, with a potential full compromise of the application’s database integrity and availability. Version 3.6.5-lts fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53639.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-vcm3-5w3f-9f45
- https://nvd.nist.gov/vuln/detail/CVE-2025-53639
