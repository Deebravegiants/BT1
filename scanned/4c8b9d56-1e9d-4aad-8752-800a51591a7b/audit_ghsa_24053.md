# [M] Jenkins Cucumber Living Documentation Plugin Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q7jx-r75r-hgj2
CVE: CVE-2018-1000144
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q7jx-r75r-hgj2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cucumber-living-documentation` — affected >=0 <1.1.0

## Details
A cross site scripting vulnerability exists in Jenkins Cucumber Living Documentation Plugin 1.0.12 and older in CukedoctorBaseAction#doDynamic that disables the Content-Security-Policy protection for archived artifacts and workspace files, allowing attackers able to control the content of these files to attack Jenkins users. This has been addressed in version 1.1.0 of the plugin, and it will now request that users change the Content-Security-Policy option in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000144
- https://github.com/jenkinsci/cucumber-living-documentation-plugin
- https://jenkins.io/security/advisory/2018-03-26/#SECURITY-308
