# [M] Jenkins Missing Permission Check

## Summary
Severity: Medium
Advisory: GHSA-wr6w-jxg7-qpfh
CVE: CVE-2025-31721
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-02
Source: https://github.com/advisories/GHSA-wr6w-jxg7-qpfh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.500 <2.504
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.492.3

## Details
Jenkins 2.503 and earlier, LTS 2.492.2 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Computer/Create permission but without Computer/Configure permission to copy an agent, gaining access to encrypted secrets in its configuration.

This is due to an incomplete fix of [SECURITY-3495](https://www.jenkins.io/security/advisory/2025-03-05/#SECURITY-3495)/CVE-2025-27622.

Jenkins 2.504, LTS 2.492.3 requires Computer/Configure permission to copy an agent containing secrets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-31721
- https://github.com/jenkinsci/jenkins/commit/b3651b475302e8dba20fc63c1ff89d144ec652f0
- https://www.jenkins.io/security/advisory/2025-04-02/#SECURITY-3513
