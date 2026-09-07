# [H] Jenkins Black Duck Hub Plugin allowed any user with Overall/Read to read and write its configuration

## Summary
Severity: High
Advisory: GHSA-crvq-mw2w-4cfx
CVE: CVE-2018-1000197
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-crvq-mw2w-4cfx
Type: github-advisory

## Affected
- Maven: `com.blackducksoftware.integration:blackduck-hub` — affected >=0 <3.1.0

## Details
An improper authorization vulnerability exists in Jenkins Black Duck Hub Plugin 3.0.3 and older in PostBuildScanDescriptor.java that allows users with Overall/Read permission to read and write the Black Duck Hub plugin configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000197
- https://jenkins.io/security/advisory/2018-05-09/#SECURITY-670
