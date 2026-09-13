# [M] Missing Authorization in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-6jfc-mc97-c7wg
CVE: CVE-2019-10354
CWE: CWE-425, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6jfc-mc97-c7wg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.176.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.177 <2.186
- Maven: `org.kohsuke.stapler:stapler-parent` — affected >=0 <1.257.1

## Details
A vulnerability in the Stapler web framework used in Jenkins 2.185 and earlier, LTS 2.176.1 and earlier allowed attackers to access view fragments directly, bypassing permission checks and possibly obtain sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10354
- https://github.com/jenkinsci/jenkins/commit/279d8109eddb7a494428baf25af9756c2e33576b
- https://github.com/jenkinsci/stapler/commit/19637555a9f32d3875356b47234131d8b1e9fee4
- https://access.redhat.com/errata/RHSA-2019:2503
- https://access.redhat.com/errata/RHSA-2019:2548
- https://jenkins.io/security/advisory/2019-07-17/#SECURITY-534
- http://www.openwall.com/lists/oss-security/2019/07/17/2
