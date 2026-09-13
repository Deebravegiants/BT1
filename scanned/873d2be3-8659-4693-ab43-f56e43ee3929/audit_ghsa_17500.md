# [M] GeoServer Missing Authorization on REST API Index

## Summary
Severity: Medium
Advisory: GHSA-h86g-x8mm-78m5
CVE: CVE-2025-27505
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-h86g-x8mm-78m5
Type: github-advisory

## Affected
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.26.0 <2.26.3
- Maven: `org.geoserver.web:gs-web-app` — affected >=0 <2.25.6
- Maven: `org.geoserver:gs-rest` — affected >=2.26.0 <2.26.3
- Maven: `org.geoserver:gs-rest` — affected >=0 <2.25.6

## Details
### Summary
It is possible to bypass the default REST API security and access the index page.

### Details
The REST API security handles `rest` and its subpaths but not `rest` with an extension (e.g., `rest.html`).

### Impact
The REST API index can disclose whether certain extensions are installed.

### Workaround
In `${GEOSERVER_DATA_DIR}/security/config.xml`, change the paths for the `rest` filter to `/rest.*,/rest/**` and change the paths for the `gwc` filter to `/gwc/rest.*,/gwc/rest/**` and restart GeoServer.

### References
https://osgeo-org.atlassian.net/browse/GEOS-11664  
https://osgeo-org.atlassian.net/browse/GEOS-11776  
https://github.com/geoserver/geoserver/pull/8170

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-h86g-x8mm-78m5
- https://nvd.nist.gov/vuln/detail/CVE-2025-27505
- https://github.com/geoserver/geoserver/pull/8170
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11664
- https://osgeo-org.atlassian.net/browse/GEOS-11776
