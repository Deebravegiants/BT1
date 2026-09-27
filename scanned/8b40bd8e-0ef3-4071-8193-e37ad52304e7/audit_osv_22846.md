# [M] Metabase's GeoJSON validation doesn't prevent redirects to blocked URLs

## Summary
Severity: Medium
Advisory: CVE-2022-39359
Aliases: GHSA-w5j7-4mgm-77f4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-39359
Type: osv

## Details
Metabase is data visualization software. Prior to versions 0.44.5, 1.44.5, 0.43.7, 1.43.7, 0.42.6, 1.42.6, 0.41.9, and 1.41.9, custom GeoJSON map URL address would follow redirects to addresses that were otherwise disallowed, like link-local or private-network. This issue is patched in versions 0.44.5, 1.44.5, 0.43.7, 1.43.7, 0.42.6, 1.42.6, 0.41.9, and 1.41.9. Metabase no longer follow redirects on GeoJSON map URLs. An environment variable `MB_CUSTOM_GEOJSON_ENABLED` was also added to disable custom GeoJSON completely (`true` by default).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39359.json
- https://github.com/metabase/metabase/security/advisories/GHSA-w5j7-4mgm-77f4
- https://nvd.nist.gov/vuln/detail/CVE-2022-39359
- https://github.com/metabase/metabase/commit/057e2d67fcbeb6b48db68b697e022243e3a5771e
