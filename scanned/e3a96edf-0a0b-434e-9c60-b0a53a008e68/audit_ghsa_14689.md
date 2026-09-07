# [M] Welcome and About GeoServer pages communicate version and revision information

## Summary
Severity: Medium
Advisory: GHSA-6pfc-w86r-54q6
CVE: CVE-2024-35230
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-12-16
Source: https://github.com/advisories/GHSA-6pfc-w86r-54q6
Type: github-advisory

## Affected
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.0.0 <2.25.1
- Maven: `org.geoserver.web:gs-web-core` — affected >=2.0.0 <2.25.1

## Details
### Impact

The welcome and about page includes version and revision information about the software in use (including library and components used).

This information is sensitive from a security point of view because it allows software used by the server to be easily identified.

### Proof of Concept

1. Welcome page footer: 
   
   <img width="432" alt="image" src="https://github.com/geoserver/geoserver/assets/629681/a7fd5151-55d5-432b-9d5d-79136833609f">

2. About page *build information*. 

   <img width="401" alt="image" src="https://github.com/geoserver/geoserver/assets/629681/59fcd8dd-eaee-4bf8-9578-a2a94b2864db">

### Patches

No patch presently available.

### Workarounds

No workaround available, although the ADMIN_CONSOLE can be disabled completely.

### References

* [About GeoServer](https://docs.geoserver.org/latest/en/user/webadmin/about.html)

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-6pfc-w86r-54q6
- https://nvd.nist.gov/vuln/detail/CVE-2024-35230
- https://github.com/geoserver/geoserver/commit/5fd5f35ae176eff3cc4667a5cf48e4bf5dc4ea99
- https://github.com/geoserver/geoserver/commit/74fdab745a5deff20ac99abca24d8695fe1a52f8
- https://github.com/geoserver/geoserver/commit/8cd1590a604a10875de67b04995f1952f631f920
- https://github.com/geoserver/geoserver
