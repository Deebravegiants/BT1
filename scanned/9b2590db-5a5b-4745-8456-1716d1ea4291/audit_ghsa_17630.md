# [H] GeoNetwork affected by XML External Entity (XXE) processing vulnerability in WFS indexing REST API endpoint

## Summary
Severity: High
Advisory: GHSA-2p76-gc46-5fvc
CWE: CWE-611, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-2p76-gc46-5fvc
Type: github-advisory

## Affected
- Maven: `org.geonetwork-opensource:gn-web-app` — affected >=4.4.0 <4.4.8
- Maven: `org.geonetwork-opensource:gn-web-app` — affected >=4.2.0 <4.2.13
- Maven: `org.geonetwork-opensource:gn-wfsfeature-harvester` — affected >=4.4.0 <4.4.8
- Maven: `org.geonetwork-opensource:gn-wfsfeature-harvester` — affected >=4.2.0 <4.2.13

## Details
### Impact

GeoNetwork WFS Index functionality is affected by GeoTools XML External Entity (XXE) vulnerability during schema validation. 

This vulnerability is particularly severe as the REST API endpoint was not secured, potentially allowing unauthenticated attackers to read sensitive files 

### Patches

GeoNetwork 4.4.8 / 4.2.13.

### Workarounds

Remove the ``gn-wfsfeature-harvester`` and ``gn-camelPeriodicProducer``  jars, disabling the WFS Index functionality. 

### References

- [GHSA-826p-4gcg-35vw](https://github.com/geotools/geotools/security/advisories/GHSA-826p-4gcg-35vw)
- https://github.com/geonetwork/core-geonetwork/pull/8757
- https://github.com/geonetwork/core-geonetwork/pull/8803
- https://github.com/geonetwork/core-geonetwork/pull/8812

## References
- https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-2p76-gc46-5fvc
- https://github.com/geotools/geotools/security/advisories/GHSA-826p-4gcg-35vw
- https://github.com/geonetwork/core-geonetwork/pull/8757
- https://github.com/geonetwork/core-geonetwork/pull/8803
- https://github.com/geonetwork/core-geonetwork/pull/8812
- https://github.com/geonetwork/core-geonetwork
