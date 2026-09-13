# [C] Directus <12.1.0 - Authenticated time-based SQL injection in PostgreSQL/PostGIS collection creation

## Summary
Severity: Critical
Advisory: CVE-2026-10716
Aliases: GHSA-chfm-g7r3-vv42
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-10716
Type: osv

## Details
Directus contains an authenticated SQL injection vulnerability in the collection creation flow when the instance uses PostgreSQL with PostGIS enabled. An administrator can create a collection with a geometry field whose fields[].type value starts with geometry but contains attacker-controlled SQL syntax after the geometry subtype.This issue affects Directus: before 12.1.0.

## References
- https://fluidattacks.com/es/advisories/metallica
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10716.json
- https://github.com/directus/directus/security/advisories/GHSA-chfm-g7r3-vv42
- https://nvd.nist.gov/vuln/detail/CVE-2026-10716
- https://github.com/directus/directus/releases#release-v12.1.0
- https://github.com/directus/directus
