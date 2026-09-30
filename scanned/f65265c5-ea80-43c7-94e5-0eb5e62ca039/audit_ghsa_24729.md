# [M] Missing permissions check in Jenkins Core

## Summary
Severity: Medium
Advisory: GHSA-59fm-6x3q-q3q5
CVE: CVE-2016-3725
CWE: CWE-280
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-59fm-6x3q-q3q5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.3

## Details
Jenkins before 2.3 and LTS before 1.651.2 allows remote authenticated users to trigger updating of update site metadata by leveraging a missing permissions check. NOTE: this issue can be combined with DNS cache poisoning to cause a denial of service (service disruption).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3725
- https://access.redhat.com/errata/RHSA-2016:1206
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-05-11
- https://www.cloudbees.com/jenkins-security-advisory-2016-05-11
- http://rhn.redhat.com/errata/RHSA-2016-1773.html
