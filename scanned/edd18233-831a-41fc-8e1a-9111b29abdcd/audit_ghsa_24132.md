# [M] Jenkins has XML External Entity (XXE) Vulnerability in Job Configuration via CLI

## Summary
Severity: Medium
Advisory: GHSA-3j9c-cp7m-8w8g
CVE: CVE-2015-5319
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3j9c-cp7m-8w8g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.626 <1.638
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.625.2

## Details
XML external entity (XXE) vulnerability in the create-job CLI command in Jenkins before 1.638 and LTS before 1.625.2 allows remote attackers to read arbitrary files via a crafted job configuration that is then used in an "XML-aware tool," as demonstrated by get-job and update-job.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5319
- https://github.com/jenkinsci/jenkins/commit/e78e9e8144f7304cf274cd4b756f458cf63a3556
- https://access.redhat.com/errata/RHSA-2016:0070
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-11-11
- http://rhn.redhat.com/errata/RHSA-2016-0489.html
