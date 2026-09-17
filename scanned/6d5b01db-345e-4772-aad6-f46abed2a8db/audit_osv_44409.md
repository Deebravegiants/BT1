# [H] Budibase before 3.41.3 Authorization Bypass via datasources/query

## Summary
Severity: High
Advisory: CVE-2026-82239
Aliases: GHSA-vq3j-xwg3-pg8x
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82239
Type: osv

## Details
Budibase before 3.41.3 fails to enforce per-table role restrictions on the POST /api/datasources/query endpoint, allowing low-privilege BASIC users to read, create, update, or delete rows in any table regardless of configured permissions. Attackers with BASIC role can submit crafted query requests with target table identifiers to bypass table-level access controls and manipulate restricted data.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-vq3j-xwg3-pg8x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82239.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82239
- https://www.vulncheck.com/advisories/budibase-before-3.41.3-authorization-bypass-via-datasources-query
