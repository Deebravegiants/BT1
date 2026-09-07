# [M] GeoServer has a Reflected Cross-Site Scripting (XSS) vulnerability in its WMS GetFeatureInfo HTML format

## Summary
Severity: Medium
Advisory: GHSA-w66h-j855-qr72
CVE: CVE-2025-21621
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-w66h-j855-qr72
Type: github-advisory

## Affected
- Maven: `org.geoserver.web:gs-web-app` — affected >=0 <2.25.0
- Maven: `org.geoserver:gs-wms` — affected >=0 <2.25.0

## Details
### Summary
A reflected cross-site scripting (XSS) vulnerability exists in the WMS GetFeatureInfo HTML output format that enables a remote attacker to execute arbitrary JavaScript code in a victim's browser through specially crafted SLD_BODY parameters. 

### Details

The WMS service setting that controls HTML auto-escaping is either disabled by default, or completely missing, in the affected versions (see workarounds).

### Impact

If an attacker can control a script that is executed in the victim's browser, then they can typically fully compromise that user. Amongst other things, the attacker can:
1. Perform any action within the application that the user can perform.
2. View any information that the user is able to view.
3. Modify any information that the user is able to modify.
4. Initiate interactions with other application users, including malicious attacks, that will appear to originate from the initial victim user.

### Workarounds
Changing any of the following WMS service settings should mitigate this vulnerability in most environments:
1. Enable GetFeatureInfo HTML auto-escaping (available in GeoServer 2.21.3+ and 2.22.1+)
2. Disable dynamic styling
3. Disable GetFeatureInfo text/html MIME type

### References
https://osgeo-org.atlassian.net/browse/GEOS-11297
https://github.com/geoserver/geoserver/pull/7406

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-w66h-j855-qr72
- https://nvd.nist.gov/vuln/detail/CVE-2025-21621
- https://github.com/geoserver/geoserver/pull/7406
- https://github.com/geoserver/geoserver/commit/dc9ff1c726dd73c884437a123b4ad72b19383c7d
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11203
- https://osgeo-org.atlassian.net/browse/GEOS-11297
