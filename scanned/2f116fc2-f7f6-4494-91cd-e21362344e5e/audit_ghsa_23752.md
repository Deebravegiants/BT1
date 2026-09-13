# [M] Exposure of sensitive information vulnerability in Jenkins Black Duck Hub Plugin

## Summary
Severity: Medium
Advisory: GHSA-26hw-262c-g9gc
CVE: CVE-2018-1000190
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-26hw-262c-g9gc
Type: github-advisory

## Affected
- Maven: `com.blackducksoftware.integration:blackduck-hub` — affected >=0 <4.0.1

## Details
A exposure of sensitive information vulnerability exists in Jenkins Black Duck Hub Plugin 4.0.0 and older in PostBuildScanDescriptor.java that allows attackers with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000190
- https://jenkins.io/security/advisory/2018-06-04/#SECURITY-865
