# [M] Jenkins allows Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: GHSA-449q-v4j2-5h8p
CVE: CVE-2015-5320
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-449q-v4j2-5h8p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.626 <1.638
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.625.2

## Details
Jenkins before 1.638 and LTS before 1.625.2 do not properly verify the shared secret used in JNLP slave connections, which allows remote attackers to connect as slaves and obtain sensitive information or possibly gain administrative access by leveraging knowledge of the name of a slave.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5320
- https://access.redhat.com/errata/RHSA-2016:0070
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-11-11
- http://rhn.redhat.com/errata/RHSA-2016-0489.html
