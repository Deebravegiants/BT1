# [C] GeoServer OGC Filter SQL Injection Vulnerabilities

## Summary
Severity: Critical
Advisory: GHSA-7g5f-wrx8-5ccf
CVE: CVE-2023-25157
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-22
Source: https://github.com/advisories/GHSA-7g5f-wrx8-5ccf
Type: github-advisory

## Affected
- Maven: `org.geoserver.community:gs-jdbcconfig` — affected >=0 <2.21.4
- Maven: `org.geoserver.community:gs-jdbcconfig` — affected >=2.22.0 <2.22.2

## Details
### Impact

GeoServer includes support for the OGC Filter expression language and the OGC Common Query Language (CQL) as part of the Web Feature Service (WFS) and Web Map Service (WMS) protocols.  CQL is also supported through the Web Coverage Service (WCS) protocol for ImageMosaic coverages.

SQL Injection Vulnerabilities have been found with:

* ``PropertyIsLike`` filter, when used with a String field and any database DataStore, or with a PostGIS DataStore with encode functions enabled
* ``strEndsWith`` function, when used with a PostGIS DataStore with encode functions enabled
* ``strStartsWith`` function, when used with a PostGIS DataStore with encode functions enabled
* ``FeatureId`` filter, when used with any database table having a String primary key column and when prepared statements are disabled
* ``jsonArrayContains`` function, when used with a String or JSON field and with a PostGIS or Oracle DataStore (GeoServer 2.22.0+ only)
* ``DWithin`` filter, when used with an Oracle DataStore

### Patches

* GeoSever 2.21.4
* GeoServer 2.22.2
* GeoServer 2.20.7
* GeoServer 2.19.7
* GeoServer 2.18.7

### Workarounds

1. Disabling the PostGIS Datastore *encode functions* setting to mitigate ``strEndsWith``, ``strStartsWith`` vulnerabilities (Like filters have no mitigation, if there is a string field in the feature type published).
2. Enabling the PostGIS DataStore *preparedStatements* setting to mitigate the ``FeatureId`` vulnerability.

### References

* [OGC Filter SQL Injection Vulnerabilities](https://github.com/geotools/geotools/security/advisories/GHSA-99c3-qc2q-p94m) (GeoTools)
* [OGC Filter Injection Vulnerability Statement](https://geoserver.org/vulnerability/2023/02/20/ogc-filter-injection.html) (GeoServer Blog)

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-7g5f-wrx8-5ccf
- https://nvd.nist.gov/vuln/detail/CVE-2023-25157
- https://github.com/geoserver/geoserver/commit/145a8af798590288d270b240235e89c8f0b62e1d
- https://github.com/geoserver/geoserver
