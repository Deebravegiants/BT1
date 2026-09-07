# [M] GeoServer's GWC Seed Form vulnerable to Stored Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-56r3-f536-5gf7
CVE: CVE-2024-23643
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-56r3-f536-5gf7
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-gwc-rest` — affected >=0 <2.23.2
- Maven: `org.geoserver:gs-gwc-rest` — affected >=2.24.0 <2.24.1

## Details
### Summary
A stored cross-site scripting (XSS) vulnerability exists that enables an authenticated administrator with workspace-level privileges to store a JavaScript payload in the GeoServer catalog that will execute in the context of another administrator’s browser when viewed in the GWC Seed Form.  Access to the GWC Seed Form is limited to full administrators by default and granting non-administrators access to this endpoint is not recommended.

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
https://github.com/GeoWebCache/geowebcache/issues/1172
https://github.com/GeoWebCache/geowebcache/pull/1174

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-56r3-f536-5gf7
- https://nvd.nist.gov/vuln/detail/CVE-2024-23643
- https://github.com/GeoWebCache/geowebcache/issues/1172
- https://github.com/GeoWebCache/geowebcache/pull/1174
- https://github.com/GeoWebCache/geowebcache/commit/9d010e09c784690ada8af43f594461a2553a62f0
- https://github.com/GeoWebCache/geowebcache/commit/c0ca08a20bc0e66dafbdb083f7508b372c0703ee
- https://github.com/geoserver/geoserver
