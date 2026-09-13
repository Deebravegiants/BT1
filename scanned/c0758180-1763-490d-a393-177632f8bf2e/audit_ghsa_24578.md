# [M] Jenkins Promoted Builds Plugin allowed unauthorized users to run some promotion processes

## Summary
Severity: Medium
Advisory: GHSA-9rx5-w522-5fh7
CVE: CVE-2018-1000114
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9rx5-w522-5fh7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:promoted-builds` — affected >=0 <3.0

## Details
An improper authorization vulnerability exists in Jenkins Promoted Builds Plugin 2.31.1 and earlier in Status.java and ManualCondition.java that allow an attacker with read access to jobs to perform promotions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000114
- https://jenkins.io/security/advisory/2018-02-26/#SECURITY-746
