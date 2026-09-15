# [M] Jenkins does not invalidate the API token when a user is deleted

## Summary
Severity: Medium
Advisory: GHSA-vxc6-wvh8-fpxw
CVE: CVE-2014-2062
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vxc6-wvh8-fpxw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.533 <1.551
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.532.2

## Details
Jenkins before 1.551 and LTS before 1.532.2 does not invalidate the API token when a user is deleted, which allows remote authenticated users to retain access via the token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2062
- https://github.com/jenkinsci/jenkins/commit/5548b5220cfd496831b5721124189ff18fbb12a3
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-02-14
- http://www.openwall.com/lists/oss-security/2014/02/21/2
