# [C] GeoTools OGC Filter SQL Injection Vulnerabilities

## Summary
Severity: Critical
Advisory: GHSA-99c3-qc2q-p94m
CVE: CVE-2023-25158
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-22
Source: https://github.com/advisories/GHSA-99c3-qc2q-p94m
Type: github-advisory

## Affected
- Maven: `org.geotools:gt-jdbc` — affected >=28.0 <28.2
- Maven: `org.geotools:gt-jdbc` — affected >=27.0 <27.4
- Maven: `org.geotools:gt-jdbc` — affected >=26.0 <26.7
- Maven: `org.geotools:gt-jdbc` — affected >=25.0 <25.7
- Maven: `org.geotools:gt-jdbc` — affected >=0 <24.7

## Details
### Impact

GeoTools includes support for OGC Filter expression language parsing, encoding and execution against a range of datastore.

SQL Injection Vulnerabilities have been found when executing OGC Filters with JDBCDataStore implementations:

1. ``PropertyIsLike`` filter
   * Requires PostGIS DataStore with "encode functions" enabled
   * Or any JDBCDataStore (all relational databases) with String field (no mitigation)
3. ``strEndsWith`` function
   * Requires PostGIS DataStore with "encode functions" enabled
5. ``strStartsWith`` function
   * Requires PostGIS DataStore with "encode functions" enabled
6. ``FeatureId`` filter
   * Requires JDBCDataStore (all relational databases) with prepared statements disabled and table with String primary key (Oracle not affected, SQL Server and MySQL have no settings to enabled prepared statements, PostGIS does)
7. ``jsonArrayContains`` function
   * Requires PostGIS and Oracle DataStore with String or JSON field
8. ``DWithin`` filter
   * Happens only in Oracle DataStore, no mitigation

### Patches

* GeoTools 28.2
* GeoTools 27.4
* GeoTools 26.7
* GeoTools 25.7
* GeoTools 24.7

### Workarounds

Partial mitigation:

* In PostGIS DataStore disable "encode functions"
* In any PostGIS enable "prepared statements" (only database with such settings)

```java
        Map<String, Object> params = new HashMap<>();
        params.put("dbtype", "postgis");
        params.put("host", "localhost");
        params.put("port", 5432);
        params.put("schema", "public");
        params.put("database", "database");
        params.put("user", "postgres");
        params.put("passwd", "postgres");
        params.put("preparedStatements", true ); // mitigation
        params.put("encode functions", false ); // mitigation

        DataStore dataStore = DataStoreFinder.getDataStore(params);
```

### References

* [OGC Filter SQL Injection Vulnerabilities](https://github.com/geoserver/geoserver/security/advisories/GHSA-7g5f-wrx8-5ccf) (GeoServer)

## References
- https://github.com/geotools/geotools/security/advisories/GHSA-99c3-qc2q-p94m
- https://nvd.nist.gov/vuln/detail/CVE-2023-25158
- https://github.com/geotools/geotools/commit/64fb4c47f43ca818c2fe96a94651bff1b3b3ed2b
- https://github.com/geotools/geotools
