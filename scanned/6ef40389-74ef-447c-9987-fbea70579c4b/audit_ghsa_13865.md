# [C] java-xmlbuilder vulnerable to XML External Entity Reference

## Summary
Severity: Critical
Advisory: GHSA-3vrc-rrpw-r5pw
CVE: CVE-2014-125087
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-19
Source: https://github.com/advisories/GHSA-3vrc-rrpw-r5pw
Type: github-advisory

## Affected
- Maven: `com.jamesmurty.utils:java-xmlbuilder` — affected >=0 <1.2

## Details
A vulnerability was found in java-xmlbuilder up to 1.1. It has been rated as problematic. Affected by this issue is some unknown functionality. The manipulation leads to xml external entity reference. Upgrading to version 1.2 is able to address this issue. The name of the patch is e6fddca201790abab4f2c274341c0bb8835c3e73. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-221480.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-125087
- https://github.com/jmurty/java-xmlbuilder/issues/6
- https://github.com/jmurty/java-xmlbuilder/commit/e6fddca201790abab4f2c274341c0bb8835c3e73
- https://github.com/jmurty/java-xmlbuilder
- https://github.com/jmurty/java-xmlbuilder/releases/tag/v1.2
- https://security.netapp.com/advisory/ntap-20240208-0009
- https://vuldb.com/?ctiid.221480
- https://vuldb.com/?id.221480
