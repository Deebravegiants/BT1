# [M] Personal tokens stored in plain text by Jenkins incapptic connect uploader Plugin

## Summary
Severity: Medium
Advisory: GHSA-8g9w-5jv6-7m4x
CVE: CVE-2022-27218
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-8g9w-5jv6-7m4x
Type: github-advisory

## Affected
- Maven: `com.incapptic.plugins:incapptic-connect-uploader` — affected >=0

## Details
Jenkins incapptic connect uploader Plugin 1.15 and earlier stores tokens unencrypted in job config.xml files on the Jenkins controller where they can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27218
- https://github.com/jenkinsci/incapptic-connect-uploader-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2273
- http://www.openwall.com/lists/oss-security/2022/03/15/2
