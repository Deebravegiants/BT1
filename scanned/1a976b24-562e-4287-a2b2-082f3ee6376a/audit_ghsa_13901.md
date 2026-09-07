# [H] dd-plist XML External Entitly vulnerability

## Summary
Severity: High
Advisory: GHSA-4jx2-hvqw-93j9
CVE: CVE-2016-15026
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-20
Source: https://github.com/advisories/GHSA-4jx2-hvqw-93j9
Type: github-advisory

## Affected
- Maven: `com.googlecode.plist:dd-plist` — affected >=0 <1.18

## Details
A vulnerability was found in 3breadt dd-plist 1.17 and classified as problematic. Affected by this issue is some unknown functionality. The manipulation leads to xml external entity reference. An attack has to be approached locally. Upgrading to version 1.18 is able to address this issue. The name of the patch is 8c954e8d9f6f6863729e50105a8abf3f87fff74c. It is recommended to upgrade the affected component. VDB-221486 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-15026
- https://github.com/3breadt/dd-plist/pull/26
- https://github.com/3breadt/dd-plist/commit/8c954e8d9f6f6863729e50105a8abf3f87fff74c
- https://github.com/3breadt/dd-plist
- https://github.com/3breadt/dd-plist/releases/tag/dd-plist-1.18
- https://vuldb.com/?ctiid.221486
- https://vuldb.com/?id.221486
