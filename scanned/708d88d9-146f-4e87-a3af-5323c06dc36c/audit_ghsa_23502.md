# [M] XML External Entity processing vulnerability in Jenkins Black Duck Hub Plugin

## Summary
Severity: Medium
Advisory: GHSA-8rc4-3jc3-83pm
CVE: CVE-2018-1000198
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8rc4-3jc3-83pm
Type: github-advisory

## Affected
- Maven: `com.blackducksoftware.integration:blackduck-hub` — affected >=0 <4.0.0

## Details
A XML external entity processing vulnerability exists in Jenkins Black Duck Hub Plugin 3.1.0 and older in PostBuildScanDescriptor.java that allows attackers with Overall/Read permission to make Jenkins process XML eternal entities in an XML document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000198
- https://jenkins.io/security/advisory/2018-05-09/#SECURITY-671
