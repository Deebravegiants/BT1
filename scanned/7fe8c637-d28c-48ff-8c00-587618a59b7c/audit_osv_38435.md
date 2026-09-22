# [M] Information about ECS zero scoped answers might leak to clients that use a specific ECS

## Summary
Severity: Medium
Advisory: CVE-2026-40012
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-40012
Type: osv

## Details
ECS zero scoped answers are stored in the packet cache while they should not. This impacts only configurations that have ECS enabled;

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-powerdns-2026-08.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40012.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40012
- https://github.com/PowerDNS/pdns
