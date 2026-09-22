# [C] Metabase: Unsafe Deserialization of H2 Query Results

## Summary
Severity: Critical
Advisory: CVE-2026-59827
Aliases: GHSA-w95f-x9v9-wv36
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-59827
Type: osv

## Details
Metabase is an open-source business intelligence and embedded analytics tool. Prior to 1.58.15, 1.59.12, 1.60.6.3, and 1.61.1.4, Metabase instances with an H2 database connection, including the default sample database, deserialize arbitrary Java objects returned in H2 native query result columns of type OTHER without validation, allowing an authenticated user who can run native H2 queries to execute code on the Metabase server. This issue is fixed in versions 1.58.15, 1.59.12, 1.60.6.3, and 1.61.1.4.

## References
- https://github.com/metabase/metabase/releases/tag/v0.58.15
- https://github.com/metabase/metabase/releases/tag/v0.59.12
- https://github.com/metabase/metabase/releases/tag/v0.60.6.3
- https://github.com/metabase/metabase/releases/tag/v0.61.1.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59827.json
- https://github.com/metabase/metabase/security/advisories/GHSA-w95f-x9v9-wv36
- https://nvd.nist.gov/vuln/detail/CVE-2026-59827
- https://github.com/metabase/metabase/commit/00f42511fe3bc4385652a2e96862ee6fd7d42cf8
