# [M] Windmill Labs Windmill - Missing Authorization

## Summary
Severity: Medium
Advisory: CVE-2026-72541
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72541
Type: osv

## Details
A missing authorization vulnerability in Windmill Labs Windmill through 1.783.0 allows any authenticated workspace member to overwrite any resource type schema via the update_resource_type endpoint. The endpoint omits the administrator permission check that the corresponding delete_resource_type endpoint enforces. An attacker with workspace member privileges can corrupt resource type definitions, breaking workflows that depend on them.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72541.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72541
- https://github.com/windmill-labs/windmill
