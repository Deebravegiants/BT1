# [C] AWS SDK is vulnerable to server-side request forgery (SSRF) 

## Summary
Severity: Critical
Advisory: GHSA-f5h9-qx38-2hgp
CVE: CVE-2022-4725
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-f5h9-qx38-2hgp
Type: github-advisory

## Affected
- Maven: `com.amazonaws:aws-android-sdk-mobile-client` — affected >=0 <2.59.1

## Details
A vulnerability was found in AWS SDK 2.59.0. It has been rated as critical. This issue affects the function XpathUtils of the file aws-android-sdk-core/src/main/java/com/amazonaws/util/XpathUtils.java of the component XML Parser. The manipulation leads to server-side request forgery. Upgrading to version 2.59.1 can address this issue. The name of the patch is c3e6d69422e1f0c80fe53f2d757b8df97619af2b. It is recommended to upgrade the affected component. The identifier VDB-216737 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4725
- https://github.com/aws-amplify/aws-sdk-android/pull/3100
- https://github.com/aws-amplify/aws-sdk-android/commit/c3e6d69422e1f0c80fe53f2d757b8df97619af2b
- https://github.com/aws-amplify/aws-sdk-android
- https://github.com/aws-amplify/aws-sdk-android/releases/tag/release_v2.59.1
- https://vuldb.com/?id.216737
