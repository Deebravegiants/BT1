# [M] GeoServer's Simple SVG Renderer vulnerable to Stored Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-fg9v-56hw-g525
CVE: CVE-2024-23642
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-fg9v-56hw-g525
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-wms` — affected >=0 <2.23.4
- Maven: `org.geoserver:gs-wms` — affected >=2.24.0 <2.24.1

## Details
### Summary
A stored cross-site scripting (XSS) vulnerability exists that enables an authenticated administrator with workspace-level privileges to store a JavaScript payload in the GeoServer catalog that will execute in the context of another user's browser when viewed in the WMS GetMap SVG Output Format when the Simple SVG renderer is enabled.  Access to the WMS SVG Format is available to all users by default although data and service security may limit users' ability to trigger the XSS.

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._

### Impact
If an attacker can control a script that is executed in the victim's browser, then they can typically fully compromise that user. Amongst other things, the attacker can:

1 .Perform any action within the application that the user can perform.
2. View any information that the user is able to view.
3. Modify any information that the user is able to modify.
4. Initiate interactions with other application users, including malicious attacks, that will appear to originate from the initial victim user.

### References
https://osgeo-org.atlassian.net/browse/GEOS-11152
https://github.com/geoserver/geoserver/pull/7173

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-fg9v-56hw-g525
- https://nvd.nist.gov/vuln/detail/CVE-2024-23642
- https://github.com/geoserver/geoserver/pull/7173
- https://github.com/geoserver/geoserver/commit/1b1835afbb9c282d1840786259aeda81c1d22b00
- https://github.com/geoserver/geoserver/commit/9f40265febb5939f23e2c53930c9c35e93970afe
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11152
