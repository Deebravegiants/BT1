# [M] GeoNetwork search end-point information disclosure in response headers

## Summary
Severity: Medium
Advisory: GHSA-52rf-25hq-5m33
CVE: CVE-2024-32037
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-02-11
Source: https://github.com/advisories/GHSA-52rf-25hq-5m33
Type: github-advisory

## Affected
- Maven: `org.geonetwork-opensource:gn-services` — affected >=4.4.0 <4.4.5
- Maven: `org.geonetwork-opensource:gn-services` — affected >=0 <4.2.10

## Details
### Impact

The search end-point response headers contain information about Elasticsearch software in use. This information is sensitive from a security point of view because it allows software used by the server to be easily identified.

### Patches

GeoNetwork 4.4.5 / 4.2.10

### Workarounds

None

### References
- [CVE-2024-32037](https://www.cve.org/CVERecord?id=CVE-2024-32037)
- [Search service](https://docs.geonetwork-opensource.org/4.4/api/search/)

### Credits

- [Ministry of Economic Affairs and Climate Policy](https://www.rijksoverheid.nl/ministeries/ministerie-van-economische-zaken-en-klimaat), The Netherlands.

## References
- https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-52rf-25hq-5m33
- https://nvd.nist.gov/vuln/detail/CVE-2024-32037
- https://docs.geonetwork-opensource.org/4.4/api/search
- https://github.com/geonetwork/core-geonetwork
- https://github.com/geonetwork/core-geonetwork/releases/tag/4.2.10
- https://github.com/geonetwork/core-geonetwork/releases/tag/4.4.5
- https://www.cve.org/CVERecord?id=CVE-2024-32037
