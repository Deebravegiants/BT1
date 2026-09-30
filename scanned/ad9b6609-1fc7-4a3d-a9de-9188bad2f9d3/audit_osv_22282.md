# [H] Unchecked JNDI lookups in GeoTools

## Summary
Severity: High
Advisory: CVE-2022-24818
Aliases: GHSA-jvh2-668r-g75x
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-04-13
Source: https://osv.dev/vulnerability/CVE-2022-24818
Type: osv

## Details
GeoTools is an open source Java library that provides tools for geospatial data. The GeoTools library has a number of data sources that can perform unchecked JNDI lookups, which in turn can be used to perform class deserialization and result in arbitrary code execution. Similar to the Log4J case, the vulnerability can be triggered if the JNDI names are user-provided, but requires admin-level login to be triggered. The lookups are now restricted in GeoTools 26.4, GeoTools 25.6, and GeoTools 24.6. Users unable to upgrade should ensure that any downstream application should not allow usage of remotely provided JNDI strings.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24818.json
- https://github.com/geotools/geotools/security/advisories/GHSA-jvh2-668r-g75x
- https://nvd.nist.gov/vuln/detail/CVE-2022-24818
- https://github.com/geotools/geotools/commit/4f70fa3234391dd0cda883a20ab0ec75688cba49
