# [M] GeoServer's GWC Demos Page vulnerable to Stored Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-88wc-fcj9-q3r9
CVE: CVE-2024-23821
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-88wc-fcj9-q3r9
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-gwc` — affected >=2.24.0 <2.24.1
- Maven: `org.geoserver:gs-gwc` — affected >=0 <2.23.4

## Details
### Summary
A stored cross-site scripting (XSS) vulnerability exists that enables an authenticated administrator with workspace-level privileges to store a JavaScript payload in the GeoServer catalog that will execute in the context of another user's browser when viewed in the GWC Demos Page.  Access to the GWC Demos Page is available to all users although data security may limit users' ability to trigger the XSS.

### Impact
If an attacker can control a script that is executed in the victim's browser, then they can typically fully compromise that user. Amongst other things, the attacker can:

1 .Perform any action within the application that the user can perform.
2. View any information that the user is able to view.
3. Modify any information that the user is able to modify.
4. Initiate interactions with other application users, including malicious attacks, that will appear to originate from the initial victim user.

### References
https://github.com/GeoWebCache/geowebcache/issues/1171
https://github.com/GeoWebCache/geowebcache/pull/1173

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-88wc-fcj9-q3r9
- https://nvd.nist.gov/vuln/detail/CVE-2024-23821
- https://github.com/GeoWebCache/geowebcache/issues/1171
- https://github.com/GeoWebCache/geowebcache/pull/1173
- https://github.com/geoserver/geoserver
