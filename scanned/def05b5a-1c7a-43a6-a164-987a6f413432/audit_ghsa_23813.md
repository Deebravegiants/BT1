# [H] Jenkins does not Verify Checksums for Plugin Files

## Summary
Severity: High
Advisory: GHSA-x274-9m9r-fm5g
CVE: CVE-2015-7539
CWE: CWE-345
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x274-9m9r-fm5g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.625.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.626 <1.640

## Details
The Plugins Manager in Jenkins before 1.640 and LTS before 1.625.2 does not verify checksums for plugin files referenced in update site data, which makes it easier for man-in-the-middle attackers to execute arbitrary code via a crafted plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7539
- https://github.com/jenkinsci/jenkins/commit/11479a2cc0a322a6bcd7e65667f3d24aa4d444bb
- https://github.com/jenkinsci/jenkins/commit/97adb71aa4509f91e408a16ba312e817ec015cf4
- https://github.com/jenkinsci/jenkins/commit/9ec88357a354d8354728cc06e2b8c8b68aee58bf
- https://github.com/jenkinsci/jenkins/commit/c158648afa8888bc49ac337c973d4e4bc050118e
- https://github.com/jenkinsci/jenkins/commit/f99cb46e06f394637067730a82f46bddc3567295
- https://access.redhat.com/errata/RHSA-2016:0070
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-12-09
- http://rhn.redhat.com/errata/RHSA-2016-0489.html
