# [M] Jenkins QMetry for JIRA Plugin stored credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-8mjp-8c2x-3g7w
CVE: CVE-2019-16544
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8mjp-8c2x-3g7w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:qmetry-for-jira-test-management` — affected >=0 <1.13

## Details
Jenkins QMetry for JIRA - Test Management Plugin stored credentials unencrypted in job config.xml files on the Jenkins controller as part of its post-build step configuration. This credential could be viewed by users with Extended Read permission or access to the Jenkins controller file system.

QMetry for JIRA - Test Management Plugin now stores these credentials encrypted once the job configuration is saved again.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16544
- https://jenkins.io/security/advisory/2019-11-21/#SECURITY-727%20(1)
- http://www.openwall.com/lists/oss-security/2019/11/21/1
