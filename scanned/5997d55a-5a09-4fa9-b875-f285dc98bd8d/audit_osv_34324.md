# [M] GeoServer has a Server-Side Request Forgery (SSRF) Vulnerability in its XML Entity Resolution

## Summary
Severity: Medium
Advisory: CVE-2025-58175
Aliases: GHSA-x4r9-gmw3-hxww
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2025-58175
Type: osv

## Details
GeoServer is an open source server that allows users to share and edit geospatial data. Prior to versions 2.26.4 and 2.27.3, a GeoServer that uses `ENTITY_RESOLUTION_ALLOWLIST` may allow attacker to perform unauthenticated Server-Side Request Forgery (SSRF). This vulnerability requires that GeoServer is set up to use a proxy base URL and the `ENTITY_RESOLUTION_ALLOWLIST` (default since 2.25.0). Versions 2.26.4 and 2.27.3 contain a fix. GeoServer installations are only affected by this vulnerability if they use a proxy base URL that does not contain a URL path or end with a slash. If the proxy base URL does not contain a path, adding a slash to the end of the URL will mitigate this vulnerability.

## References
- https://osgeo-org.atlassian.net/browse/GEOS-11867
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58175.json
- https://github.com/geoserver/geoserver/security/advisories/GHSA-x4r9-gmw3-hxww
- https://nvd.nist.gov/vuln/detail/CVE-2025-58175
- https://github.com/geoserver/geoserver/pull/8622
