# [C] GeoTools has unauthenticated SQL injection in the jsonArrayContains filter function against PostGIS layers

## Summary
Severity: Critical
Advisory: GHSA-mqjf-5f49-2fjh
CVE: CVE-2026-76904
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-mqjf-5f49-2fjh
Type: github-advisory

## Affected
- Maven: `org.geotools.jdbc:gt-jdbc-postgis` — affected >=35.0 <35.1
- Maven: `org.geotools.jdbc:gt-jdbc-postgis` — affected >=34.0 <34.5
- Maven: `org.geotools.jdbc:gt-jdbc-postgis` — affected >=30.5 <33.6

## Details
### Summary

An SQL Injection Vulnerability has been found when executing OGC Filters with PostGIS DataStore implementation:

* `jsonArrayContains` function  
    Requires PostGIS 12 or greater with a String or JSON field

For PostGIS 12 and greater `jsonArrayContains(<column>, <pointer>, <value>)` function writes `<value>` into generated SQL without escaping.

### Patches

* GeoTools 35.1
* GeoTools 33.5
* GeoTools 34.4

### Mitigation

No mitigation is available:

* To limit scope of SQL Injection the PostGIS connection pool should be configured with limited rights.

### Impact

This vulnerability can lead to execution of arbitrary SQL expressions in the database.

### References

* https://osgeo-org.atlassian.net/browse/GEOT-7958
* https://osgeo-org.atlassian.net/browse/GEOT-7959
* https://github.com/geotools/geotools/pull/5829
* https://osgeo-org.atlassian.net/browse/GEOT-7589

## References
- https://github.com/geotools/geotools/security/advisories/GHSA-mqjf-5f49-2fjh
- https://github.com/geotools/geotools/pull/5829
- https://github.com/geotools/geotools/commit/d821c4d321dd91c22e31fcd5b1ce676645da5176
- https://github.com/geotools/geotools
- https://github.com/geotools/geotools/releases/tag/33.6
- https://github.com/geotools/geotools/releases/tag/34.5
- https://github.com/geotools/geotools/releases/tag/35.1
- https://osgeo-org.atlassian.net/browse/GEOT-7589
- https://osgeo-org.atlassian.net/browse/GEOT-7958
- https://osgeo-org.atlassian.net/browse/GEOT-7959
