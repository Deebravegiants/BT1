# [M] GeoServer's Style Publisher vulnerable to Stored Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-9rfr-pf2x-g4xf
CVE: CVE-2024-23640
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-9rfr-pf2x-g4xf
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-main` — affected >=0 <2.23.3
- Maven: `org.geoserver:gs-ows` — affected >=0 <2.23.3

## Details
### Summary
A stored cross-site scripting (XSS) vulnerability exists that enables an authenticated administrator with workspace-level privileges to store a JavaScript payload in uploaded style/legend resources or in a specially crafted datastore file that will execute in the context of another user's browser when viewed in the Style Publisher.  Access to the Style Publisher is available to all users although data security may limit users' ability to trigger the XSS.

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
https://osgeo-org.atlassian.net/browse/GEOS-11149
https://github.com/geoserver/geoserver/pull/7162
https://osgeo-org.atlassian.net/browse/GEOS-11155
https://github.com/geoserver/geoserver/pull/7181

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-9rfr-pf2x-g4xf
- https://nvd.nist.gov/vuln/detail/CVE-2024-23640
- https://github.com/geoserver/geoserver/pull/7162
- https://github.com/geoserver/geoserver/pull/7181
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11149
- https://osgeo-org.atlassian.net/browse/GEOS-11155
