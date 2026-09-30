# [C] CVE-2026-53676

## Summary
Severity: Critical
Advisory: CVE-2026-53676
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-53676
Type: osv

## Details
ThingsBoard contains a prototype pollution vulnerability which may lead to arbitrary code execution within a sandboxed context by a user who can log in to the affected product with the tenant administrator privilege (TENANT_ADMIN).

## References
- https://jvn.jp/en/jp/JVN16937365/
- https://thingsboard.io/docs/releases/releases-table/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53676.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53676
- https://github.com/thingsboard/thingsboard/pull/15600
