# [M] GeoServer's WMS OpenLayers Format vulnerable to Stored Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-fcpm-hchj-mh72
CVE: CVE-2024-23818
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-fcpm-hchj-mh72
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-wms` — affected >=0 <2.23.3
- Maven: `org.geoserver:gs-wms` — affected >=2.24.0 <2.24.1

## Details
### Summary
A stored cross-site scripting (XSS) vulnerability exists that enables an authenticated administrator with workspace-level privileges to store a JavaScript payload in the GeoServer catalog that will execute in the context of another user's browser when viewed in the WMS GetMap OpenLayers Output Format.  Access to the WMS OpenLayers Format is available to all users by default although data and service security may limit users' ability to trigger the XSS.

### Impact
If an attacker can control a script that is executed in the victim's browser, then they can typically fully compromise that user. Amongst other things, the attacker can:

1 .Perform any action within the application that the user can perform.
2. View any information that the user is able to view.
3. Modify any information that the user is able to modify.
4. Initiate interactions with other application users, including malicious attacks, that will appear to originate from the initial victim user.

### References
https://osgeo-org.atlassian.net/browse/GEOS-11153
https://github.com/geoserver/geoserver/pull/7174

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-fcpm-hchj-mh72
- https://nvd.nist.gov/vuln/detail/CVE-2024-23818
- https://github.com/geoserver/geoserver/pull/7174
- https://github.com/geoserver/geoserver/commit/4557a832eed19ec18b9753cb97e8aa85269741d2
- https://github.com/geoserver/geoserver/commit/a26c32a469ee4c599236380452ffb4260361bd6f
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11153
