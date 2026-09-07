# [M] GeoServer's MapML HTML Page vulnerable to Stored Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-7x76-57fr-m5r5
CVE: CVE-2024-23819
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-7x76-57fr-m5r5
Type: github-advisory

## Affected
- Maven: `org.geoserver.extension:gs-mapml` — affected >=0 <2.23.4
- Maven: `org.geoserver.extension:gs-mapml` — affected >=2.24.0 <2.24.1

## Details
### Summary
A stored cross-site scripting (XSS) vulnerability exists that enables an authenticated administrator with workspace-level privileges to store a JavaScript payload in the GeoServer catalog that will execute in the context of another user's browser when viewed in the MapML HTML Page.  The MapML extension must be installed and access to the MapML HTML Page is available to all users although data security may limit users' ability to trigger the XSS.

### Impact
If an attacker can control a script that is executed in the victim's browser, then they can typically fully compromise that user. Amongst other things, the attacker can:

1 .Perform any action within the application that the user can perform.
2. View any information that the user is able to view.
3. Modify any information that the user is able to modify.
4. Initiate interactions with other application users, including malicious attacks, that will appear to originate from the initial victim user.

### References
https://osgeo-org.atlassian.net/browse/GEOS-11154
https://github.com/geoserver/geoserver/pull/7175

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-7x76-57fr-m5r5
- https://nvd.nist.gov/vuln/detail/CVE-2024-23819
- https://github.com/geoserver/geoserver/pull/7175
- https://github.com/geoserver/geoserver/commit/6f04adbdc6c289f5cb815b1462a6bd790e3fb6ef
- https://github.com/geoserver/geoserver/commit/df65ff05250cbb498c78af906d66e0c084ace8a1
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11154
