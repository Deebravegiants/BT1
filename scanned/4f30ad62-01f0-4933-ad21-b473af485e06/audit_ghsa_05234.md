# [H] GeoServer DB2 DataStore Extension has a JNDI Vulnerability via Store Connection

## Summary
Severity: High
Advisory: GHSA-g628-r368-6vh7
CVE: CVE-2025-27511
CWE: CWE-502, CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-g628-r368-6vh7
Type: github-advisory

## Affected
- Maven: `org.geoserver.extension:gs-db2` — affected >=0 <2.27.0

## Details
## Summary

Administrator can perform JNDI attack through specially crafted DB2 jdbc url leading to Remote Code Execution (RCE).

## Impact

If GeoServer has DB2 extension installed, this vulnerability can lead to executing arbitrary code.

## Details

Authenticated users can access Vector Data Sources page to creating a new data store through db2 jdbc connection, performing JNDI attack due to unrestricted connection parameters, and then achieve RCE with deserialization of untrusted data.

### Remediation

This issue has been fixed in this release: https://github.com/geoserver/geoserver/releases/tag/2.27.0.

## References

* https://osgeo-org.atlassian.net/browse/GEOT-7725
* https://nvd.nist.gov/vuln/detail/cve-2023-27867

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-g628-r368-6vh7
- https://nvd.nist.gov/vuln/detail/CVE-2025-27511
- https://github.com/geoserver/geoserver
- https://github.com/geoserver/geoserver/releases/tag/2.27.0
- https://nvd.nist.gov/vuln/detail/cve-2023-27867
- https://osgeo-org.atlassian.net/browse/GEOT-7725
