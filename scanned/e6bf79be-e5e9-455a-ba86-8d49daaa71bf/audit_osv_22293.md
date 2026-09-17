# [C] Unchecked JNDI lookups in GeoWebCache

## Summary
Severity: Critical
Advisory: CVE-2022-24846
Aliases: GHSA-4v22-v8jp-438r
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2022-24846
Type: osv

## Details
GeoWebCache is a tile caching server implemented in Java. The GeoWebCache disk quota mechanism can perform an unchecked JNDI lookup, which in turn can be used to perform class deserialization and result in arbitrary code execution. While in GeoWebCache the JNDI strings are provided via local configuration file, in GeoServer a user interface is provided to perform the same, that can be accessed remotely, and requires admin-level login to be used. These lookup are unrestricted in scope and can lead to code execution. The lookups are going to be restricted in GeoWebCache 1.21.0, 1.20.2, 1.19.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24846.json
- https://github.com/GeoWebCache/geowebcache/security/advisories/GHSA-4v22-v8jp-438r
- https://nvd.nist.gov/vuln/detail/CVE-2022-24846
