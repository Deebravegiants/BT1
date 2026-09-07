# [H] Cleartext Storage of Sensitive Information in Jenkins Extensive Testing Plugin

## Summary
Severity: High
Advisory: GHSA-8x6c-375h-pm4f
CVE: CVE-2019-10448
CWE: CWE-312, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8x6c-375h-pm4f
Type: github-advisory

## Affected
- Maven: `jenkins.xtc:extensivetesting` — affected 1.4.4b

## Details
Jenkins Extensive Testing Plugin stores credentials unencrypted in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10448
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1432
