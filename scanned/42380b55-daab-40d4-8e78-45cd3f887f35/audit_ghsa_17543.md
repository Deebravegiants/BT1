# [H] GeoServer Infinite Loop Vulnerability in Jiffle process

## Summary
Severity: High
Advisory: GHSA-gr67-pwcv-76gf
CVE: CVE-2025-30145
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-gr67-pwcv-76gf
Type: github-advisory

## Affected
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.26.0 <2.26.3
- Maven: `org.geoserver:gs-wms` — affected >=2.26.0 <2.26.3
- Maven: `org.geoserver.extension:gs-wps-core` — affected >=2.26.0 <2.26.3
- Maven: `org.geoserver.web:gs-web-app` — affected >=0 <2.25.7
- Maven: `org.geoserver:gs-wms` — affected >=0 <2.25.7
- Maven: `org.geoserver.extension:gs-wps-core` — affected >=0 <2.25.7

## Details
### Summary
Malicious Jiffle scripts can be executed by GeoServer, either as a rendering transformation in WMS dynamic styles or as a WPS process, that can enter an infinite loop to trigger denial of service.

### Details
The Jiffle language supports multiple loop constructs that will cause its code block to be continuously executed until a certain condition is met. The Jiffle runtime should be updated to throw an exception if the script exceeds a certain number of loop iterations.

### Impact
This vulnerability allows attackers to conduct denial-of-service attacks.

### Mitigation
This vulnerability can be mitigated by disabling WMS dynamic styling (see [WMS Settings](https://docs.geoserver.org/latest/en/user/services/wms/webadmin.html#disabling-usage-of-dynamic-styling-in-getmap-getfeatureinfo-and-getlegendgraphic-requests)).
If the WPS extension is installed, the Jiffle process must also be disabled to mitigate this vulnerability (see [WPS Settings](https://docs.geoserver.org/latest/en/user/services/wps/security.html#input-limits))

### References
https://github.com/geosolutions-it/jai-ext/pull/307
https://osgeo-org.atlassian.net/browse/GEOS-11778

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-gr67-pwcv-76gf
- https://nvd.nist.gov/vuln/detail/CVE-2025-30145
- https://github.com/geosolutions-it/jai-ext/pull/307
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11778
