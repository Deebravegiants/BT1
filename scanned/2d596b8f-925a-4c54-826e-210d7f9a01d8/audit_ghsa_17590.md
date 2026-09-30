# [M] GWC Home Page communicate version and revision information

## Summary
Severity: Medium
Advisory: GHSA-jm79-7xhw-6f6f
CVE: CVE-2024-38524
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-jm79-7xhw-6f6f
Type: github-advisory

## Affected
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.26.0 <2.26.2
- Maven: `org.geoserver.web:gs-web-app` — affected >=0 <2.25.6
- Maven: `org.geoserver:gs-gwc` — affected >=2.26.0 <2.26.2
- Maven: `org.geoserver:gs-gwc` — affected >=0 <2.25.6

## Details
### Summary
The GeoWebCache home page includes version and revision information about the software in use. This information is sensitive from a security point of view because it allows software used by the server to be easily identified.

### Details
org.geowebcache.GeoWebCacheDispatcher.handleFrontPage(HttpServletRequest, HttpServletResponse) has no check to hide potentially sensitive information from users except for a hidden system property to hide the storage locations that defaults to showing the locations.

### PoC
Just open http://localhost:8080/geoserver/gwc/

### Impact
In addition to exposing the version and revision information, the home page will expose the config file and storage locations which may expose the system's temp directory location and whether or not GeoServer is running in a Windows operating system. The approximate server start time and some basic GWC usage information is also exposed.

### References
https://osgeo-org.atlassian.net/browse/GEOS-11677
https://github.com/geoserver/geoserver/pull/8189
https://github.com/GeoWebCache/geowebcache/issues/1344
https://github.com/GeoWebCache/geowebcache/pull/1345

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-jm79-7xhw-6f6f
- https://nvd.nist.gov/vuln/detail/CVE-2024-38524
- https://github.com/GeoWebCache/geowebcache/issues/1344
- https://github.com/GeoWebCache/geowebcache/pull/1345
- https://github.com/geoserver/geoserver/pull/8189
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11677
