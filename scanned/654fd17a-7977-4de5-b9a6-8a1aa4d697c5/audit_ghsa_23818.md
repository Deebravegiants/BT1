# [M] Improper handling of equivalent directory names on Windows in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-6q4g-84f3-mw74
CVE: CVE-2021-21682
CWE: CWE-42
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6q4g-84f3-mw74
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.304 <2.315
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.303.2

## Details
Jenkins stores jobs and other entities on disk using their name shown on the UI as file and folder names.

On Windows, when specifying a file or folder with a trailing dot character (`example.`), the file or folder will be treated as if that character was not present (`example`). As both are legal names for jobs and other entities in Jenkins 2.314 and earlier, LTS 2.303.1 and earlier, this could allow users with the appropriate permissions to change or replace configurations of jobs and other entities.

Jenkins 2.315, LTS 2.303.2 does not allow names of jobs and other entities to end with a dot character.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21682
- https://github.com/jenkinsci/jenkins/commit/c2c2b59071265aea07f88d5e95297c0a433921c3
- https://www.jenkins.io/security/advisory/2021-10-06/#SECURITY-2424
- http://www.openwall.com/lists/oss-security/2021/10/06/1
