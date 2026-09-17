# [M] Exposure of Sensitive Information in Jenkins Core

## Summary
Severity: Medium
Advisory: GHSA-jgpr-qrw2-6gp3
CVE: CVE-2016-0790
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-jgpr-qrw2-6gp3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.650

## Details
Jenkins before 1.650 and LTS before 1.642.2 do not use a constant-time algorithm to verify API tokens, which makes it easier for remote attackers to determine API tokens via a brute-force approach.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0790
- https://access.redhat.com/errata/RHSA-2016:0711
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-02-24
- http://rhn.redhat.com/errata/RHSA-2016-1773.html
