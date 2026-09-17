# [H] Observable timing discrepancy in JOpenId

## Summary
Severity: High
Advisory: GHSA-m4f8-p58g-j8mj
CVE: CVE-2010-10006
CWE: CWE-203, CWE-208
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-18
Source: https://github.com/advisories/GHSA-m4f8-p58g-j8mj
Type: github-advisory

## Affected
- Maven: `org.expressme:JOpenId` — affected >=0 <1.08

## Details
A vulnerability, which was classified as problematic, was found in michaelliao jopenid. Affected is the function getAuthentication of the file JOpenId/src/org/expressme/openid/OpenIdManager.java. The manipulation leads to observable timing discrepancy. Upgrading to version 1.08 is able to address this issue. The name of the patch is c9baaa976b684637f0d5a50268e91846a7a719ab. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-218460.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-10006
- https://github.com/michaelliao/jopenid/commit/c9baaa976b684637f0d5a50268e91846a7a719ab
- https://github.com/michaelliao/jopenid/releases/tag/JOpenId-1.08
- https://vuldb.com/?ctiid.218460
- https://vuldb.com/?id.218460
