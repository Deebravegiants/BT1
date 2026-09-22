# [H] Improper Input Validation in GeoServer

## Summary
Severity: High
Advisory: GHSA-4pm3-f52j-8ggh
CVE: CVE-2022-24847
CWE: CWE-20, CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-4pm3-f52j-8ggh
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-main` — affected >=2.20.0 <2.20.4
- Maven: `org.geoserver:gs-main` — affected >=0 <2.19.6

## Details
### Impact
The GeoServer security mechanism can perform an unchecked JNDI lookup, which in turn can be used to perform class deserialization and result in arbitrary code execution. The same can happen while configuring data stores with data sources located in JNDI, or while setting up the disk quota mechanism.
In order to perform any of the above changes, the attack needs to have obtained admin rights and use either the GeoServer GUI, or its REST API.

### Patches
The lookups are going to be restricted in GeoServer 2.21.0, 2.20.4, 2.19.6.

### Workarounds
Protection can be achieved by making the GUI (``geoserver/web``), the REST configuration (``geoserver/rest``) and the embedded GeoWebCache configuration (``geoserver/gwc/rest``) unreachable from remote hosts, in addition to protecting access to the file system where the GeoServer configuration is stored.

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-4pm3-f52j-8ggh
- https://nvd.nist.gov/vuln/detail/CVE-2022-24847
- https://github.com/geoserver/geoserver/commit/b94a69943992df999d627b21a4ed056fad4569f8
- https://github.com/geoserver/geoserver
